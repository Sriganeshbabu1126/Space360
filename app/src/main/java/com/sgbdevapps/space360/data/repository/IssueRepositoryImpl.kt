package com.sgbdevapps.space360.data.repository

import android.util.Log
import com.sgbdevapps.space360.data.local.IssueCommentDao
import com.sgbdevapps.space360.data.local.IssueCommentEntity
import com.sgbdevapps.space360.data.local.IssueDao
import com.sgbdevapps.space360.data.local.IssueEntity
import com.sgbdevapps.space360.data.local.IssuePhotoDao
import com.sgbdevapps.space360.data.remote.AddCommentRequest
import com.sgbdevapps.space360.data.remote.IssuesService
import com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.domain.model.IssueComment
import com.sgbdevapps.space360.domain.model.IssuePhoto
import com.sgbdevapps.space360.domain.repository.IssueRepository
import javax.inject.Inject

class IssueRepositoryImpl @Inject constructor(
    private val issuesService: IssuesService,
    private val issueDao: IssueDao,
    private val commentDao: IssueCommentDao,
    private val photoDao: IssuePhotoDao
) : IssueRepository {

    override suspend fun getIssuesBySite(siteId: Int): Result<List<Issue>> {
        return try {
            val response = issuesService.getIssuesBySite(siteId)
            val issues = response.map { mapResponseToIssue(it) }

            // Cache locally
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

            Result.success(issues)
        } catch (e: Exception) {
            Log.e("IssueRepository", "Get issues by site failed: ${e.message}")
            // Fallback to local cache
            val cachedIssues = issueDao.getIssuesBySite(siteId).map { entity ->
                Issue(
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
                    updatedAt = entity.updatedAt
                )
            }
            if (cachedIssues.isNotEmpty()) {
                Result.success(cachedIssues)
            } else {
                Result.failure(e)
            }
        }
    }

    override suspend fun getIssueById(id: Int): Result<Issue> {
        return try {
            val response = issuesService.getIssueById(id)
            val issue = mapResponseToIssue(response)
            Result.success(issue)
        } catch (e: Exception) {
            Log.e("IssueRepository", "Get issue by id failed: ${e.message}")
            Result.failure(e)
        }
    }

    override suspend fun updateIssueStatus(issueId: Int, newStatus: String): Result<Issue> {
        return try {
            val response = issuesService.updateIssueStatus(issueId, UpdateIssueStatusRequest(newStatus))
            val issue = mapResponseToIssue(response)
            Result.success(issue)
        } catch (e: Exception) {
            Log.e("IssueRepository", "Update issue status failed: ${e.message}")
            Result.failure(e)
        }
    }

    override suspend fun addComment(issueId: Int, text: String): Result<Unit> {
        return try {
            issuesService.addComment(issueId, AddCommentRequest(text))
            Result.success(Unit)
        } catch (e: Exception) {
            Log.e("IssueRepository", "Add comment failed: ${e.message}")
            Result.failure(e)
        }
    }

    private fun mapResponseToIssue(response: com.sgbdevapps.space360.data.remote.IssueResponse): Issue {
        return Issue(
            id = response.id,
            title = response.title,
            description = response.description,
            siteId = response.site_id,
            status = response.status,
            priority = response.priority,
            type = response.type,
            assignedTo = response.assigned_to,
            assignedToName = response.assigned_to_name,
            createdAt = response.created_at,
            updatedAt = response.updated_at,
            comments = response.comments.map { IssueComment(it.id, it.issue_id, it.user_id, it.user_name, it.text, it.created_at) },
            photos = response.photos.map { IssuePhoto(it.id, it.issue_id, it.photo_url, it.uploaded_at) }
        )
    }
}
