$content = Get-Content F:\Space360\app\src\main\java\com\sgbdevapps\space360\data\sync\SyncWorker.kt -Raw
$content = $content -replace 'fun schedulePeriodicSync\(context: Context\) \{', "fun triggerImmediateSyncOnConnectivity(context: Context) {
            val req = OneTimeWorkRequestBuilder<SyncWorker>().build()
            WorkManager.getInstance(context).enqueue(req)
        }

        fun schedulePeriodicSync(context: Context) {"
Set-Content F:\Space360\app\src\main\java\com\sgbdevapps\space360\data\sync\SyncWorker.kt $content
