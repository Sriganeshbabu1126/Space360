package com.sgbdevapps.space360.data.sync

import android.content.Context
import androidx.hilt.work.HiltWorker
import androidx.work.*
import com.sgbdevapps.space360.data.local.Space360Database
import com.sgbdevapps.space360.data.network.NetworkConnectivityManager
import com.sgbdevapps.space360.data.remote.AddCommentRequest
import com.sgbdevapps.space360.data.remote.IssuesService
import com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.asRequestBody
import java.util.concurrent.TimeUnit

@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val database: Space360Database,
    private val issuesService: IssuesService,
    private val networkConnectivity: NetworkConnectivityManager
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        android.util.Log.e("SPACE360_DEBUG", "doWork() started")
        android.util.Log.e("SPACE360_DEBUG", "Sync worker triggered")
        if (!networkConnectivity.isConnected()) {
            android.util.Log.e("SPACE360_DEBUG", "No network connection. Retrying later.")
            return Result.retry()
        }

        return try {
            val syncQueueDao = database.syncQueueDao()
            val pendingOps = syncQueueDao.getPendingOperations()
            
            android.util.Log.e("SPACE360_DEBUG", "Found ${pendingOps.size} pending operations")

            if (pendingOps.isEmpty()) {
                return Result.success()
            }

            for (op in pendingOps) {
                try {
                    android.util.Log.e("SPACE360_DEBUG", "Processing op: ${op.operationType}")
                    when (op.operationType) {
                        "UPDATE_ISSUE_STATUS" -> {
                            val data = Json.parseToJsonElement(op.payload).jsonObject
                            val issueId = data["issueId"]?.jsonPrimitive?.content ?: continue
                            val newStatus = data["newStatus"]?.jsonPrimitive?.content ?: continue

                            issuesService.updateIssueStatus(
                                issueId,
                                UpdateIssueStatusRequest(newStatus)
                            )
                        }
                        "ADD_COMMENT" -> {
                            val data = Json.parseToJsonElement(op.payload).jsonObject
                            val issueId = data["issueId"]?.jsonPrimitive?.content ?: continue
                            val text = data["text"]?.jsonPrimitive?.content ?: continue

                            issuesService.addComment(issueId, AddCommentRequest(text))
                        }
                        "ADD_PHOTO" -> {
                            val data = Json.parseToJsonElement(op.payload).jsonObject
                            val issueId = data["issueId"]?.jsonPrimitive?.content ?: continue
                            val filePath = data["filePath"]?.jsonPrimitive?.content ?: continue
                            
                            val file = java.io.File(filePath)
                            if (file.exists()) {
                                val mediaType = "image/*".toMediaTypeOrNull()
                                val requestFile = file.asRequestBody(mediaType)
                                val body = okhttp3.MultipartBody.Part.createFormData("file", file.name, requestFile)
                                
                                issuesService.uploadPhoto(issueId, body)
                            }
                        }
                        "UPLOAD_PATH" -> {
                            android.util.Log.e("SPACE360_DEBUG", "Handling UPLOAD_PATH")
                            android.util.Log.e("SPACE360_DEBUG", "Uploading path to backend")
                            val pathId = op.payload
                            val path = database.pathDao().getPathById(pathId) ?: continue
                            val points = database.pathPointDao().getPointsForPath(pathId)
                            
                            val waypointsDto = points.map { 
                                com.sgbdevapps.space360.data.remote.WaypointDto(
                                    latitude = it.latitude,
                                    longitude = it.longitude,
                                    altitude = it.altitude,
                                    heading = it.heading,
                                    accuracy = it.accuracy,
                                    timestamp = java.time.Instant.ofEpochMilli(it.timestamp).toString()
                                )
                            }
                            
                            val request = com.sgbdevapps.space360.data.remote.CreatePathRequest(
                                siteId = path.siteId,
                                userId = path.userId,
                                startedAt = java.time.Instant.ofEpochMilli(path.startedAt).toString(),
                                endedAt = path.endedAt?.let { java.time.Instant.ofEpochMilli(it).toString() },
                                waypointCount = path.waypointCount,
                                waypoints = waypointsDto
                            )
                            
                            android.util.Log.e("SPACE360_DEBUG", "Calling createPath API...")
                            try {
                                issuesService.createPath(request)
                                android.util.Log.e("SPACE360_DEBUG", "createPath success!")
                                android.util.Log.e("SPACE360_DEBUG", "Upload complete: success")
                                database.pathDao().updatePathStatus(pathId, "UPLOADED", System.currentTimeMillis())
                            } catch (e: Exception) {
                                android.util.Log.e("SPACE360_DEBUG", "Upload complete: error - ${e.message}")
                                throw e // Re-throw to be caught by outer try-catch
                            }
                        }
                    }

                    syncQueueDao.updateOperation(
                        op.copy(
                            status = "SYNCED",
                            syncedAt = System.currentTimeMillis()
                        )
                    )
                } catch (e: Exception) {
                    android.util.Log.e("SPACE360_DEBUG", "Operation failed: ${op.operationType}", e)
                    if (e is retrofit2.HttpException) {
                        val errorBody = e.response()?.errorBody()?.string()
                        android.util.Log.e("SPACE360_DEBUG", "HTTP Error body: $errorBody")
                    }
                    val updatedOp = op.copy(
                        retryCount = op.retryCount + 1,
                        lastError = e.message,
                        lastErrorAt = System.currentTimeMillis(),
                        status = if (op.retryCount >= op.maxRetries) "FAILED" else "PENDING"
                    )
                    syncQueueDao.updateOperation(updatedOp)
                }
            }

            val sevenDaysAgo = System.currentTimeMillis() - (7 * 24 * 60 * 60 * 1000)
            syncQueueDao.deleteOldSyncedOperations(sevenDaysAgo)

            Result.success()
        } catch (e: Exception) {
            android.util.Log.e("SPACE360_DEBUG", "Sync queue execution failed", e)
            Result.retry()
        }
    }

    companion object {
        private const val SYNC_WORK_NAME = "space360_sync_queue"

        fun schedulePeriodicSync(context: Context) {
            val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
                15,
                TimeUnit.MINUTES
            ).build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                SYNC_WORK_NAME,
                ExistingPeriodicWorkPolicy.KEEP,
                syncRequest
            )
        }

        fun triggerImmediateSyncOnConnectivity(context: Context) {
            val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>().build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                "${SYNC_WORK_NAME}_immediate",
                ExistingWorkPolicy.REPLACE,
                syncRequest
            )
        }
    }
}
