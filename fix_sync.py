
with open('app/src/main/java/com/sgbdevapps/space360/data/sync/SyncWorker.kt', 'r') as f:
    content = f.read()

trigger_code = '''
        fun triggerImmediateSyncOnConnectivity(context: Context) {
            val constraints = androidx.work.Constraints.Builder()
                .setRequiredNetworkType(androidx.work.NetworkType.CONNECTED)
                .build()
            val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
                .setConstraints(constraints)
                .build()
            WorkManager.getInstance(context).enqueueUniqueWork(
                "\_immediate",
                ExistingWorkPolicy.REPLACE,
                syncRequest
            )
        }
'''

content = content.replace('    }\n}', trigger_code + '    }\n}')

content = content.replace('when (op.operationType) {', 'android.util.Log.d("SyncWorker", "Processing op: ")\n                    when (op.operationType) {')
content = content.replace('} catch (e: Exception) {', '} catch (e: Exception) {\n                    android.util.Log.e("SyncWorker", "Operation failed: ", e)')
content = content.replace('"UPLOAD_PATH" -> {', '"UPLOAD_PATH" -> {\n                            android.util.Log.d("SyncWorker", "Handling UPLOAD_PATH")')

with open('app/src/main/java/com/sgbdevapps/space360/data/sync/SyncWorker.kt', 'w') as f:
    f.write(content)

