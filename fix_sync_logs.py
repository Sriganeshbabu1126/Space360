
with open('app/src/main/java/com/sgbdevapps/space360/data/sync/SyncWorker.kt', 'r') as f:
    content = f.read()

content = content.replace('when (op.operationType) {', 'android.util.Log.d("SyncWorker", "Processing op: ")\n                    when (op.operationType) {')
content = content.replace('} catch (e: Exception) {', '} catch (e: Exception) {\n                    android.util.Log.e("SyncWorker", "Operation failed: ", e)')
content = content.replace('"UPLOAD_PATH" -> {', '"UPLOAD_PATH" -> {\n                            android.util.Log.d("SyncWorker", "Handling UPLOAD_PATH")')
content = content.replace('issuesService.createPath(request)', 'android.util.Log.d("SyncWorker", "Calling createPath API...")\n                            issuesService.createPath(request)\n                            android.util.Log.d("SyncWorker", "createPath success!")')

with open('app/src/main/java/com/sgbdevapps/space360/data/sync/SyncWorker.kt', 'w') as f:
    f.write(content)

