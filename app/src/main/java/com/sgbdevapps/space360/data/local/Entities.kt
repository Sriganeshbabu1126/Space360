package com.sgbdevapps.space360.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Int,
    val email: String,
    val displayName: String?,
    val role: String
)

@Entity(tableName = "sites")
data class SiteEntity(
    @PrimaryKey val id: Int,
    val name: String,
    val location: String,
    val status: String,
    val openIssuesCount: Int
)

@Entity(tableName = "issues")
data class IssueEntity(
    @PrimaryKey val id: Int,
    val title: String,
    val description: String,
    val siteId: Int,
    val status: String,
    val priority: String,
    val type: String,
    val assignedTo: Int,
    val assignedToName: String,
    val createdAt: String,
    val updatedAt: String
)

@Entity(tableName = "issue_comments")
data class IssueCommentEntity(
    @PrimaryKey val id: Int,
    val issueId: Int,
    val userId: Int,
    val userName: String,
    val text: String,
    val createdAt: String
)

@Entity(tableName = "issue_photos")
data class IssuePhotoEntity(
    @PrimaryKey val id: Int,
    val issueId: Int,
    val photoUrl: String,
    val uploadedAt: String
)
