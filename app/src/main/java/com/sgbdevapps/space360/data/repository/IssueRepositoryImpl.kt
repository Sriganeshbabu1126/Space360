package com.sgbdevapps.space360.data.repository

import android.util.Log
import com.sgbdevapps.space360.data.local.CacheMetadataEntity
import com.sgbdevapps.space360.data.local.IssueCommentDao
import com.sgbdevapps.space360.data.local.IssueCommentEntity
import com.sgbdevapps.space360.data.local.IssueDao
import com.sgbdevapps.space360.data.local.IssueEntity
import com.sgbdevapps.space360.data.local.IssuePhotoDao
import com.sgbdevapps.space360.data.local.IssuePhotoEntity
import com.sgbdevapps.space360.data.local.Space360Database
import com.sgbdevapps.space360.data.local.SyncQueueEntity
import com.sgbdevapps.space360.data.network.NetworkConnectivityManager
import com.sgbdevapps.space360.data.remote.AddCommentRequest
import com.sgbdevapps.space360.data.remote.IssuesService
import com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.domain.model.IssueComment
import com.sgbdevapps.space360.domain.model.IssuePhoto
import com.sgbdevapps.space360.domain.repository.IssueRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class IssueRepositoryImpl @Inject constructor(
    private val issuesService: IssuesService,
    private val database: Space360Database,
    private val networkConnectivity: NetworkConnectivityManager
) : IssueRepository {

    private val issueDao = database.issueDao()
    private val commentDao = database.issueCommentDao()
    private val photoDao = database.issuePhotoDao()
    private val syncQueueDao = database.syncQueueDao()
    private val cacheMetadataDao = database.cacheMetadataDao()

    companion object {
        private const val CACHE_TTL_ISSUES_MS = 24 * 60 * 60 * 1000L // 24 hours
    }

    override suspend fun getIssuesBySite(siteId: String, forceRefresh: Boolean): Result<List<Issue>> {
        return try {
            val cacheKey = "issues:site:$siteId"
            val now = System.currentTimeMillis()
            
            val cachedMetadata = cacheMetadataDao.getMetadata(cacheKey)
            val cacheIsValid = cachedMetadata?.expiresAt?.let { it > now } ?: false

            if (cacheIsValid && !forceRefresh) {
                val cached = issueDao.getIssuesBySite(siteId)
                if (cached.isNotEmpty()) {
                    return Result.success(cached.map { mapEntityToIssue(it) })
                }
            }

            if (networkConnectivity.isConnected()) {
                try {
                    val response = issuesService.getIssuesBySite(siteId)
                    val issues = response.map { mapResponseToIssue(it) }

                    issueDao.insertIssues(issues.map { issue ->
                        IssueEntity(
                            id = issue.id,
                            title = issue.title,
                            description = issue.description,
                            siteId = issue.siteId,
                            status = issue.status,
                            priority = issue.priority,
                            type = issue.type,
                            assignedTo = issue.assignedTo,
                            assignedToName = issue.assignedToName,
                            createdAt = issue.createdAt,
                            updatedAt = issue.updatedAt
                        )
                    })
                    
                    cacheMetadataDao.upsertMetadata(
                        CacheMetadataEntity(
                            cacheKey = cacheKey,
                            entityType = "ISSUES",
                            lastFetchedAt = now,
                            expiresAt = now + CACHE_TTL_ISSUES_MS,
                            recordCount = response.size
                        )
                    )

                    Result.success(issues)
                } catch (e: Exception) {
                    val fallback = issueDao.getIssuesBySite(siteId)
                    if (fallback.isNotEmpty()) {
                        Result.success(fallback.map { mapEntityToIssue(it) })
                    } else {
                        Result.failure(e)
                    }
                }
            } else {
                val cached = issueDao.getIssuesBySite(siteId)
                Result.success(cached.map { mapEntityToIssue(it) })
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getIssueById(id: String): Result<Issue> {
        return try {
            if (networkConnectivity.isConnected()) {
                try {
                    val response = issuesService.getIssueById(id)
                    val issue = mapResponseToIssue(response)
                    
                    // Cache issue details
                    issueDao.insertIssue(IssueEntity(
                        id = issue.id,
                        title = issue.title,
                        description = issue.description,
                        siteId = issue.siteId,
                        status = issue.status,
                        priority = issue.priority,
                        type = issue.type,
                        assignedTo = issue.assignedTo,
                        assignedToName = issue.assignedToName,
                        createdAt = issue.createdAt,
                        updatedAt = issue.updatedAt
                    ))
                    
                    commentDao.deleteCommentsByIssue(id)
                    commentDao.insertComments(issue.comments.map { 
                        IssueCommentEntity(it.id, it.issueId, it.userId, it.userName, it.text, it.createdAt) 
                    })
                    
                    photoDao.deletePhotosByIssue(id)
                    photoDao.insertPhotos(issue.photos.map { 
                        IssuePhotoEntity(it.id, it.issueId, it.photoUrl, it.uploadedAt) 
                    })
                    
                    Result.success(issue)
                } catch (e: Exception) {
                    fallbackToCache(id, e)
                }
            } else {
                fallbackToCache(id, Exception("Offline"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private suspend fun fallbackToCache(id: String, e: Exception): Result<Issue> {
        val cached = issueDao.getIssueById(id)
        if (cached != null) {
            val comments = commentDao.getCommentsByIssue(id).map { 
                IssueComment(it.id, it.issueId, it.userId, it.userName, it.text, it.createdAt) 
            }
            val photos = photoDao.getPhotosByIssue(id).map { 
                IssuePhoto(it.id, it.issueId, it.photoUrl, it.uploadedAt) 
            }
            return Result.success(mapEntityToIssue(cached).copy(comments = comments, photos = photos))
        }
        return Result.failure(e)
    }

    override suspend fun updateIssueStatus(issueId: String, newStatus: String, contractorId: String): Result<Issue> {
        return try {
            val now = System.currentTimeMillis()

            val cached = issueDao.getIssueById(issueId)
            if (cached != null) {
                issueDao.insertIssue(cached.copy(status = newStatus, syncStatus = "PENDING"))
            }

            val payload = Json.encodeToString(
                mapOf(
                    "operationType" to "UPDATE_ISSUE_STATUS",
                    "issueId" to issueId.toString(),
                    "newStatus" to newStatus,
                    "userId" to contractorId.toString(),
                    "timestamp" to now.toString()
                )
            )

            syncQueueDao.insertOperation(
                SyncQueueEntity(
                    operationType = "UPDATE_ISSUE_STATUS",
                    issueId = issueId,
                    payload = payload,
                    createdAt = now,
                    status = "PENDING"
                )
            )

            if (networkConnectivity.isConnected()) {
                syncSingleOperation(issueId, "UPDATE_ISSUE_STATUS")
            }
            
            getIssueById(issueId)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun addComment(issueId: String, text: String, contractorId: String): Result<Unit> {
        return try {
            val now = System.currentTimeMillis()

            val tempComment = IssueCommentEntity(
                id = java.util.UUID.randomUUID().toString(),
                issueId = issueId,
                userId = contractorId,
                userName = "Current User",
                text = text,
                createdAt = java.time.Instant.now().toString()
            )
            commentDao.insertComment(tempComment)

            val payload = Json.encodeToString(
                mapOf(
                    "operationType" to "ADD_COMMENT",
                    "issueId" to issueId.toString(),
                    "text" to text,
                    "userId" to contractorId.toString(),
                    "timestamp" to now.toString()
                )
            )

            syncQueueDao.insertOperation(
                SyncQueueEntity(
                    operationType = "ADD_COMMENT",
                    issueId = issueId,
                    payload = payload,
                    createdAt = now,
                    status = "PENDING"
                )
            )

            if (networkConnectivity.isConnected()) {
                syncSingleOperation(issueId, "ADD_COMMENT")
            }
            
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun addPhotoToIssue(issueId: String, filePath: String): Result<Unit> {
        return try {
            val now = System.currentTimeMillis()
            
            val tempPhoto = IssuePhotoEntity(
                id = java.util.UUID.randomUUID().toString(),
                issueId = issueId,
                photoUrl = filePath,
                uploadedAt = java.time.Instant.now().toString()
            )
            photoDao.insertPhotos(listOf(tempPhoto))
            
            val payload = Json.encodeToString(
                mapOf(
                    "operationType" to "ADD_PHOTO",
                    "issueId" to issueId.toString(),
                    "filePath" to filePath,
                    "timestamp" to now.toString()
                )
            )
            
            syncQueueDao.insertOperation(
                SyncQueueEntity(
                    operationType = "ADD_PHOTO",
                    issueId = issueId,
                    payload = payload,
                    createdAt = now,
                    status = "PENDING"
                )
            )
            
            if (networkConnectivity.isConnected()) {
                syncSingleOperation(issueId, "ADD_PHOTO")
            }
            
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun observePendingSyncCount(): Flow<Int> {
        return syncQueueDao.observePendingCount()
    }

    private suspend fun syncSingleOperation(
        issueId: String,
        operationType: String
    ): Boolean {
        return try {
            val ops = syncQueueDao.getPendingOperations()
                .filter { it.issueId == issueId && it.operationType == operationType }
            
            for (op in ops) {
                when (op.operationType) {
                    "UPDATE_ISSUE_STATUS" -> {
                        val data = Json.parseToJsonElement(op.payload).jsonObject
                        val newStatus = data["newStatus"]?.jsonPrimitive?.content ?: return false
                        
                        issuesService.updateIssueStatus(
                            issueId,
                            UpdateIssueStatusRequest(newStatus)
                        )
                        
                        val issue = issueDao.getIssueById(issueId)
                        if (issue != null) {
                            issueDao.insertIssue(issue.copy(syncStatus = "SYNCED"))
                        }
                    }
                    "ADD_COMMENT" -> {
                        val data = Json.parseToJsonElement(op.payload).jsonObject
                        val text = data["text"]?.jsonPrimitive?.content ?: return false
                        
                        issuesService.addComment(
                            issueId,
                            AddCommentRequest(text)
                        )
                    }
                    "ADD_PHOTO" -> {
                        val data = Json.parseToJsonElement(op.payload).jsonObject
                        val filePath = data["filePath"]?.jsonPrimitive?.content ?: return false
                        
                        val file = File(filePath)
                        if (file.exists()) {
                            val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())
                            val body = MultipartBody.Part.createFormData("file", file.name, requestFile)
                            
                            issuesService.uploadPhoto(issueId, body)
                        }
                    }
                }
                
                syncQueueDao.updateOperation(
                    op.copy(
                        status = "SYNCED",
                        syncedAt = System.currentTimeMillis()
                    )
                )
            }
            true
        } catch (e: Exception) {
            handleSyncFailure(issueId, operationType, e)
            false
        }
    }

    private suspend fun handleSyncFailure(
        issueId: String,
        operationType: String,
        error: Exception
    ) {
        val ops = syncQueueDao.getPendingOperations()
            .filter { it.issueId == issueId && it.operationType == operationType }
        
        for (op in ops) {
            val newStatus = if (op.retryCount >= op.maxRetries) "FAILED" else "PENDING"
            val updatedOp = op.copy(
                retryCount = op.retryCount + 1,
                lastError = error.message,
                lastErrorAt = System.currentTimeMillis(),
                status = newStatus
            )
            syncQueueDao.updateOperation(updatedOp)
            
            if (newStatus == "FAILED" && operationType == "UPDATE_ISSUE_STATUS") {
                val issue = issueDao.getIssueById(issueId)
                if (issue != null) {
                    issueDao.insertIssue(issue.copy(syncStatus = "FAILED"))
                }
            }
        }
    }

    private fun mapResponseToIssue(response: com.sgbdevapps.space360.data.remote.IssueResponse): Issue {
        return Issue(
            id = response.id,
            title = response.title,
            description = response.description ?: "",
            siteId = response.site_id,
            status = response.status,
            priority = response.priority ?: "Medium",
            type = response.type,
            assignedTo = response.assigned_to ?: "",
            assignedToName = response.assigned_to_name ?: "Unassigned",
            createdAt = response.created_at,
            updatedAt = response.updated_at,
            comments = response.comments?.map { IssueComment(it.id, it.issue_id, it.user_id, it.user_name, it.text, it.created_at) } ?: emptyList(),
            photos = response.photos?.map { IssuePhoto(it.id, it.issue_id, it.photo_url, it.uploaded_at) } ?: emptyList()
        )
    }

    private fun mapEntityToIssue(entity: IssueEntity): Issue {
        return Issue(
            id = entity.id,
            title = entity.title,
            description = entity.description,
            siteId = entity.siteId,
            status = entity.status,
            priority = entity.priority,
            type = entity.type,
            assignedTo = entity.assignedTo,
            assignedToName = entity.assignedToName,
            createdAt = entity.createdAt,
            updatedAt = entity.updatedAt,
            comments = emptyList(),
            photos = emptyList(),
            syncStatus = entity.syncStatus
        )
    }
}
