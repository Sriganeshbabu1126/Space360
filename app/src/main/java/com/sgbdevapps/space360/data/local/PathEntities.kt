package com.sgbdevapps.space360.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "paths")
data class PathEntity(
    @PrimaryKey val id: String,
    val siteId: String,
    val userId: String,
    val startedAt: Long,
    val endedAt: Long?,
    val waypointCount: Int,
    val uploadedAt: Long?,
    val status: String // RECORDING, COMPLETED, UPLOADED
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
