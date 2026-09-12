package com.sgbdevapps.space360.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "offline_sync_queue")
data class OfflineSyncQueueEntity(
    @PrimaryKey
    val id: String = UUID.randomUUID().toString(),
    
    val action: String,
    val resourceType: String,
    val resourceId: String,
    val payload: String,
    
    val status: String = "pending",
    val attempts: Int = 0,
    val maxAttempts: Int = 5,
    val lastAttemptAt: Long? = null,
    val errorMessage: String? = null,
    
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
