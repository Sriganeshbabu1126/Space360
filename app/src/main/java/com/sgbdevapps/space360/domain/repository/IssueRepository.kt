package com.sgbdevapps.space360.domain.repository

import com.sgbdevapps.space360.domain.model.Issue
import kotlinx.coroutines.flow.Flow

interface IssueRepository {
    suspend fun getIssuesBySite(siteId: Int, forceRefresh: Boolean = false): Result<List<Issue>>
    suspend fun getIssueById(id: Int): Result<Issue>
    suspend fun updateIssueStatus(issueId: Int, newStatus: String, contractorId: Int): Result<Issue>
    suspend fun addComment(issueId: Int, text: String, contractorId: Int): Result<Unit>
    suspend fun addPhotoToIssue(issueId: Int, filePath: String): Result<Unit>
    
    fun observePendingSyncCount(): Flow<Int>
}
