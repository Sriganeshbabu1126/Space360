package com.sgbdevapps.space360.domain.repository

import kotlinx.coroutines.flow.Flow

interface PathRepository {
    suspend fun startRecordingPath(siteId: String, userId: String): String
    suspend fun stopRecordingPath(pathId: String)
    suspend fun addWaypoint(pathId: String, lat: Double, lng: Double, alt: Double?, head: Double?, acc: Float)
    fun observeWaypointCount(pathId: String): Flow<Int>
    suspend fun discardPath(pathId: String)
}
