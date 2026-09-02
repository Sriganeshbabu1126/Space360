$content = Get-Content F:\Space360\app\src\main\java\com\sgbdevapps\space360\data\sync\SyncWorker.kt -Raw
$content = $content -replace 'fun triggerImmediateSync\(context: Context\).*', "fun triggerImmediateSyncOnConnectivity(context: Context) {
            val constraints = androidx.work.Constraints.Builder()
                .setRequiredNetworkType(androidx.work.NetworkType.CONNECTED)
                .build()
                
            val syncRequest = androidx.work.OneTimeWorkRequestBuilder<SyncWorker>()
                .setConstraints(constraints)
                .build()
                
            androidx.work.WorkManager.getInstance(context).enqueue(syncRequest)
        }
    }
}"
Set-Content F:\Space360\app\src\main\java\com\sgbdevapps\space360\data\sync\SyncWorker.kt $content
