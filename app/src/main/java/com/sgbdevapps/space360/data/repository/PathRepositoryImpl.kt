package com.sgbdevapps.space360.data.repository

import com.sgbdevapps.space360.data.local.PathDao
import com.sgbdevapps.space360.data.local.PathEntity
import com.sgbdevapps.space360.data.local.PathPointDao
import com.sgbdevapps.space360.data.local.PathPointEntity
import com.sgbdevapps.space360.data.local.SyncQueueDao
import com.sgbdevapps.space360.data.local.SyncQueueEntity
import com.sgbdevapps.space360.domain.repository.PathRepository
import kotlinx.coroutines.flow.Flow
import java.util.UUID

import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject

class PathRepositoryImpl @Inject constructor(
    private val pathDao: PathDao,
    private val pathPointDao: PathPointDao,
    private val syncQueueDao: SyncQueueDao,
    @ApplicationContext private val context: Context
) : PathRepository {

    override suspend fun startRecordingPath(siteId: String, userId: String): String {
        val pathId = UUID.randomUUID().toString()
        android.util.Log.e("SPACE360_DEBUG", "Creating PathEntity: [$siteId, $userId, startedAt, endedAt, waypointCount]")
        val path = PathEntity(
            id = pathId,
            siteId = siteId,
            userId = userId,
            startedAt = System.currentTimeMillis(),
            endedAt = null,
            waypointCount = 0,
            uploadedAt = null,
            status = "RECORDING"
        )
        android.util.Log.e("SPACE360_DEBUG", "Inserting into pathDao...")
        try {
            pathDao.insertPath(path)
            android.util.Log.e("SPACE360_DEBUG", "Path inserted successfully with ID: $pathId")
        } catch(e: Exception) {
            android.util.Log.e("SPACE360_DEBUG", "Failed to insert path: ${e.message}")
            throw e
        }
        return pathId
    }

    override suspend fun stopRecordingPath(pathId: String) {
        val path = pathDao.getPathById(pathId)
        if (path == null) {
            android.util.Log.e("SPACE360_DEBUG", "stopRecordingPath failed: path not found in DB for $pathId")
            return
        }
        val endedAt = System.currentTimeMillis()
        val points = pathPointDao.getPointsForPath(pathId)
        val updatedPath = path.copy(
            endedAt = endedAt,
            waypointCount = points.size,
            status = "COMPLETED"
        )
        android.util.Log.e("SPACE360_DEBUG", "Creating PathEntity: [${updatedPath.siteId}, ${updatedPath.userId}, ${updatedPath.startedAt}, ${updatedPath.endedAt}, ${updatedPath.waypointCount}]")
        android.util.Log.e("SPACE360_DEBUG", "Inserting into pathDao...")
        try {
            pathDao.insertPath(updatedPath)
            android.util.Log.e("SPACE360_DEBUG", "Path inserted successfully with ID: $pathId")
        } catch(e: Exception) {
            android.util.Log.e("SPACE360_DEBUG", "Failed to insert path: ${e.message}")
            throw e
        }
        
        android.util.Log.e("SPACE360_DEBUG", "Path saved to DB: $pathId")
        
        // Queue for sync
        val syncOp = SyncQueueEntity(
            operationType = "UPLOAD_PATH",
            issueId = pathId,
            payload = pathId,
            createdAt = System.currentTimeMillis(),
            status = "PENDING"
        )
        syncQueueDao.insertOperation(syncOp)
        android.util.Log.e("SPACE360_DEBUG", "Path queued in SyncQueue: $pathId")
        
        com.sgbdevapps.space360.data.sync.SyncWorker.triggerImmediateSyncOnConnectivity(context)
    }

    override suspend fun addWaypoint(
        pathId: String,
        lat: Double,
        lng: Double,
        alt: Double?,
        head: Double?,
        acc: Float
    ) {
        val point = PathPointEntity(
            id = UUID.randomUUID().toString(),
            pathId = pathId,
            latitude = lat,
            longitude = lng,
            altitude = alt,
            heading = head,
            accuracy = acc,
            timestamp = System.currentTimeMillis()
        )
        
        android.util.Log.e("SPACE360_DEBUG", "Inserting 1 waypoint into pathPointDao... lat/lng/timestamp")
        try {
            pathPointDao.insertPathPoint(point)
            android.util.Log.e("SPACE360_DEBUG", "Waypoint inserted successfully")
            
            // Also log: "Waypoint captured: [count] - lat/lng/timestamp"
            val points = pathPointDao.getPointsForPath(pathId)
            android.util.Log.e("SPACE360_DEBUG", "Waypoint captured: ${points.size} - $lat/$lng/${point.timestamp}")
        } catch (e: Exception) {
            android.util.Log.e("SPACE360_DEBUG", "Failed to insert waypoint: ${e.message}")
            throw e
        }
    }

    override fun observeWaypointCount(pathId: String): Flow<Int> {
        return pathPointDao.observeWaypointCount(pathId)
    }

    override suspend fun discardPath(pathId: String) {
        // Simple discard by setting status to DISCARDED
        pathDao.updatePathStatus(pathId, "DISCARDED", null)
    }
}
