package com.sgbdevapps.space360.service

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.util.Log
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.asRequestBody
import com.sgbdevapps.space360.data.local.Space360Database
import com.sgbdevapps.space360.data.remote.IssuesService
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton
import com.sgbdevapps.space360.data.local.SyncQueueEntity
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest
import com.sgbdevapps.space360.data.remote.AddCommentRequest
import dagger.hilt.android.qualifiers.ApplicationContext

@Singleton
class OfflineSyncManager @Inject constructor(
    private val api: IssuesService,
    private val db: Space360Database,
    @ApplicationContext private val context: Context
) {
    private val logger = "OfflineSyncManager"
    
    suspend fun queueAction(
        action: String,
        resourceType: String,
        resourceId: String,
        payload: Any
    ) {
        val jsonPayload = try {
            when (payload) {
                is UpdateIssueStatusRequest -> Json.encodeToString(payload)
                is AddCommentRequest -> Json.encodeToString(payload)
                is String -> payload // directly use the string for file paths
                else -> "{}"
            }
        } catch (e: Exception) { "{}" }
        
        val queueItem = SyncQueueEntity(
            operationType = action,
            issueId = resourceId,
            payload = jsonPayload,
            createdAt = System.currentTimeMillis(),
            status = "PENDING"
        )
        db.syncQueueDao().insertOperation(queueItem)
    }
    
    suspend fun syncPendingItems(): SyncResult {
        if (!isNetworkAvailable()) {
            return SyncResult(synced = 0, failed = 0, queued = 0)
        }
        
        val pendingItems = db.syncQueueDao().getPendingOperations()
        var synced = 0
        var failed = 0
        
        for (item in pendingItems) {
            try {
                when (item.operationType) {
                    "update_status" -> {
                        val update = Json.decodeFromString<UpdateIssueStatusRequest>(item.payload)
                        api.updateIssueStatus(item.issueId, update)
                    }
                    "add_comment" -> {
                        val comment = Json.decodeFromString<AddCommentRequest>(item.payload)
                        api.addComment(item.issueId, comment)
                    }
                    "upload_photo" -> {
                        val photoFilePath = item.payload.removePrefix("file://")
                        val photoFile = java.io.File(photoFilePath)
                        if (photoFile.length() > 5 * 1024 * 1024) {
                            throw Exception("Photo file too large (${photoFile.length() / 1024 / 1024} MB). Max 5MB allowed.")
                        }
                        
                        val requestFile = photoFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
                        val body = okhttp3.MultipartBody.Part.createFormData("file", photoFile.name, requestFile)
                        api.uploadPhoto(item.issueId, body)
                    }
                }
                
                item.copy(
                    status = "SYNCED",
                    syncedAt = System.currentTimeMillis()
                ).let { db.syncQueueDao().updateOperation(it) }
                
                db.syncQueueDao().deleteOperation(item)
                synced++
                
            } catch (e: Exception) {
                Log.e(logger, "Sync failed for ${item.id}", e)
                item.copy(
                    status = if (item.retryCount >= item.maxRetries) "FAILED" else "PENDING",
                    retryCount = item.retryCount + 1,
                    lastErrorAt = System.currentTimeMillis(),
                    lastError = e.message
                ).let { db.syncQueueDao().updateOperation(it) }
                
                failed++
            }
        }
        
        return SyncResult(synced, failed, db.syncQueueDao().getPendingOperations().size)
    }
    
    suspend fun getPendingItemsForResource(resourceType: String, resourceId: String): List<SyncQueueEntity> {
        return db.syncQueueDao().getPendingOperations().filter { it.issueId == resourceId }
    }

    private fun isNetworkAvailable(): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}

data class SyncResult(
    val synced: Int,
    val failed: Int,
    val queued: Int
)
