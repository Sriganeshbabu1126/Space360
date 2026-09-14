package com.sgbdevapps.space360.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "paths")
data class PathEntity(
    @PrimaryKey val id: String = java.util.UUID.randomUUID().toString(),
    val siteId: String,
    val userId: String,
    val startedAt: Long,
    val endedAt: Long?,
    val waypointCount: Int = 0,
    val uploadedAt: Long? = null,
    val status: String, // RECORDING, COMPLETED, UPLOADED
    
    // EXISTING TIMESTAMP FIELDS (from Week 1)
    val pathStartTimestampNanos: Long = 0,
    val pathEndTimestampNanos: Long = 0,
    
    // NEW FIELDS (Week 2 — Camera + Clock Metadata)
    val cameraStartTimestampNanos: Long? = null,
    val cameraEndTimestampNanos: Long? = null,
    val clockOffsetNanos: Long? = null,
    val recordingSessionJson: String? = null,
    
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "path_points")
data class PathPointEntity(
    @PrimaryKey val id: String,
    val pathId: String,
    val latitude: Double,
    val longitude: Double,
    val altitude: Double?,
    val heading: Double?,
    val accuracy: Float,
    val timestamp: Long
)
