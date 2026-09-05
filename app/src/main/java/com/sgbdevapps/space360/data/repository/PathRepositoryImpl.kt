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
        pathDao.insertPath(path)
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
        pathDao.insertPath(updatedPath)
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
        pathPointDao.insertPathPoint(point)
    }

    override fun observeWaypointCount(pathId: String): Flow<Int> {
        return pathPointDao.observeWaypointCount(pathId)
    }

    override suspend fun discardPath(pathId: String) {
        // Simple discard by setting status to DISCARDED
        pathDao.updatePathStatus(pathId, "DISCARDED", null)
    }
}
