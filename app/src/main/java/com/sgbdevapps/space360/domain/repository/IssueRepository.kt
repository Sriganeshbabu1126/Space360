package com.sgbdevapps.space360.domain.repository

import com.sgbdevapps.space360.domain.model.Issue
import kotlinx.coroutines.flow.Flow

interface IssueRepository {
    suspend fun getIssuesBySite(siteId: String? = null, forceRefresh: Boolean = false): Result<List<Issue>>
    suspend fun getIssueById(id: String): Result<Issue>
    suspend fun updateIssueStatus(issueId: String, newStatus: String, contractorId: String): Result<Issue>
    suspend fun addComment(issueId: String, text: String, contractorId: String): Result<Unit>
    suspend fun addPhotoToIssue(issueId: String, filePath: String): Result<Unit>
    
    fun observePendingSyncCount(): Flow<Int>
}
