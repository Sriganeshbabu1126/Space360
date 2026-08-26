package com.sgbdevapps.space360.domain.repository

import com.sgbdevapps.space360.domain.model.Issue

interface IssueRepository {
    suspend fun getIssuesBySite(siteId: Int): Result<List<Issue>>
    suspend fun getIssueById(id: Int): Result<Issue>
    suspend fun updateIssueStatus(issueId: Int, newStatus: String): Result<Issue>
    suspend fun addComment(issueId: Int, text: String): Result<Unit>
}
