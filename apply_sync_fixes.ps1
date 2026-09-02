$content = Get-Content F:\Space360\app\src\main\java\com\sgbdevapps\space360\data\sync\SyncWorker.kt -Raw
$content = $content -replace 'for \(op in pendingOps\) \{', "for (op in pendingOps) {
                android.util.Log.d("SyncWorker", "Processing op: $($op.operationType)")"
$content = $content -replace '\} catch \(e: Exception\) \{', "} catch (e: Exception) {
                    android.util.Log.e("SyncWorker", "Op failed: $($op.operationType)", e)"
$content = $content -replace '"UPLOAD_PATH" -> \{', ""UPLOAD_PATH" -> {
                            android.util.Log.d("SyncWorker", "Handling UPLOAD_PATH")"
$content = $content -replace 'issuesService\.createPath\(request\)', "android.util.Log.d("SyncWorker", "Calling createPath")
                            issuesService.createPath(request)
                            android.util.Log.d("SyncWorker", "createPath success")"
$content = $content -replace 'ExistingPeriodicWorkPolicy\.KEEP,?
\s*syncRequest?
\s*\)?
\s*\}', "ExistingPeriodicWorkPolicy.KEEP,
                syncRequest
            )
        }

        fun triggerImmediateSyncOnConnectivity(context: android.content.Context) {
            val req = androidx.work.OneTimeWorkRequestBuilder<SyncWorker>().build()
            androidx.work.WorkManager.getInstance(context).enqueue(req)
        }"
Set-Content F:\Space360\app\src\main\java\com\sgbdevapps\space360\data\sync\SyncWorker.kt $content
