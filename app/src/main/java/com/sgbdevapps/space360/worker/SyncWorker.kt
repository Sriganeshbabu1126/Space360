package com.sgbdevapps.space360.worker

import android.content.Context
import androidx.hilt.work.HiltWorker
import androidx.work.*
import com.sgbdevapps.space360.service.OfflineSyncManager
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import java.util.concurrent.TimeUnit
import android.util.Log

@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val offlineSyncManager: OfflineSyncManager
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        return try {
            val result = offlineSyncManager.syncPendingItems()
            
            if (result.failed > 0) {
                Log.w("SyncWorker", "Sync partial failure: ${result.synced} synced, ${result.failed} failed")
            } else if (result.queued > 0) {
                Log.i("SyncWorker", "Sync queued ${result.queued} items, will retry later")
            }
            
            Result.success()
        } catch (e: Exception) {
            Log.e("SyncWorker", "Sync worker failed", e)
            Result.retry()
        }
    }
    
    companion object {
        fun schedulePeriodicSync(context: Context) {
            val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
                15, TimeUnit.MINUTES
            ).setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            ).build()
            
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                "offline_sync",
                ExistingPeriodicWorkPolicy.KEEP,
                syncRequest
            )
        }
    }
}
