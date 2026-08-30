package com.sgbdevapps.space360.domain.model

data class Issue(
    val id: String,
    val title: String,
    val description: String,
    val siteId: String,
    val status: String = "Open", // Open, In Review, Pending, Closed, Critical
    val priority: String = "Medium", // Low, Medium, High, Critical
    val type: String = "defect", // defect, safety_issue, quality_issue, incomplete_work, rework_required
    val assignedTo: String,
    val assignedToName: String,
    val createdAt: String,
    val updatedAt: String,
    val comments: List<IssueComment> = emptyList(),
    val photos: List<IssuePhoto> = emptyList(),
    val syncStatus: String? = null
)

data class IssueComment(
    val id: String,
    val issueId: String,
    val userId: String,
    val userName: String,
    val text: String,
    val createdAt: String
)

data class IssuePhoto(
    val id: String,
    val issueId: String,
    val photoUrl: String,
    val uploadedAt: String
)
