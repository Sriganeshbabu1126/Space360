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

@Entity(
    tableName = "issues",
    indices = [
        androidx.room.Index("siteId"),
        androidx.room.Index("assignedTo"),
        androidx.room.Index("status"),
        androidx.room.Index("updatedAt")
    ],
    foreignKeys = [
        androidx.room.ForeignKey(
            entity = SiteEntity::class,
            parentColumns = ["id"],
            childColumns = ["siteId"],
            onDelete = androidx.room.ForeignKey.CASCADE
        )
    ]
)
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
    val updatedAt: String,
    val syncStatus: String? = null
)

@Entity(
    tableName = "sync_queue",
    indices = [
        androidx.room.Index("issueId"),
        androidx.room.Index("createdAt"),
        androidx.room.Index("syncedAt")
    ]
)
data class SyncQueueEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    val operationType: String,
    val issueId: Int,
    val payload: String,
    
    val createdAt: Long,
    val syncedAt: Long? = null,
    
    val retryCount: Int = 0,
    val maxRetries: Int = 5,
    val lastError: String? = null,
    val lastErrorAt: Long? = null,
    
    val status: String = "PENDING"
)

@Entity(
    tableName = "cache_metadata",
    indices = [androidx.room.Index("entityType"), androidx.room.Index("expiresAt")]
)
data class CacheMetadataEntity(
    @PrimaryKey
    val cacheKey: String,
    
    val entityType: String,
    val lastFetchedAt: Long,
    val expiresAt: Long,
    val recordCount: Int = 0
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
