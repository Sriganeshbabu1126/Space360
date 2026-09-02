$content = Get-Content F:\Space360\app\src\main\java\com\sgbdevapps\space360\data\sync\SyncWorker.kt -Raw
$content = $content -replace '(?s)companion object \{.*', "companion object {
        private const val SYNC_WORK_NAME = "space360_sync_queue"

        fun schedulePeriodicSync(context: Context) {
            val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
                15,
                java.util.concurrent.TimeUnit.MINUTES
            ).build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                SYNC_WORK_NAME,
                ExistingPeriodicWorkPolicy.KEEP,
                syncRequest
            )
        }

        fun triggerImmediateSyncOnConnectivity(context: Context) {
            val req = OneTimeWorkRequestBuilder<SyncWorker>().build()
            WorkManager.getInstance(context).enqueue(req)
        }
    }
}"
Set-Content F:\Space360\app\src\main\java\com\sgbdevapps\space360\data\sync\SyncWorker.kt $content
