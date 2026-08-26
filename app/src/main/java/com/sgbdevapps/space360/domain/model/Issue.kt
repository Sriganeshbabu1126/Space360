package com.sgbdevapps.space360.domain.model

data class Issue(
    val id: Int,
    val title: String,
    val description: String,
    val siteId: Int,
    val status: String = "Open", // Open, In Review, Pending, Closed, Critical
    val priority: String = "Medium", // Low, Medium, High, Critical
    val type: String = "defect", // defect, safety_issue, quality_issue, incomplete_work, rework_required
    val assignedTo: Int,
    val assignedToName: String,
    val createdAt: String,
    val updatedAt: String,
    val comments: List<IssueComment> = emptyList(),
    val photos: List<IssuePhoto> = emptyList()
)

data class IssueComment(
    val id: Int,
    val issueId: Int,
    val userId: Int,
    val userName: String,
    val text: String,
    val createdAt: String
)

data class IssuePhoto(
    val id: Int,
    val issueId: Int,
    val photoUrl: String,
    val uploadedAt: String
)
