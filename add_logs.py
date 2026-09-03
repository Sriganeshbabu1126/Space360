
with open('app/src/main/java/com/sgbdevapps/space360/data/repository/PathRepositoryImpl.kt', 'r') as f:
    content = f.read()

content = content.replace('syncQueueDao.insertOperation(syncOp)', 'android.util.Log.d("PathRepo", "Saving path \ to DB and queueing for sync")\n        syncQueueDao.insertOperation(syncOp)')
content = content.replace('triggerImmediateSyncOnConnectivity(context)', 'android.util.Log.d("PathRepo", "Enqueueing immediate SyncWorker")\n        com.sgbdevapps.space360.data.sync.SyncWorker.triggerImmediateSyncOnConnectivity(context)')

with open('app/src/main/java/com/sgbdevapps/space360/data/repository/PathRepositoryImpl.kt', 'w') as f:
    f.write(content)

with open('app/src/main/java/com/sgbdevapps/space360/data/sync/SyncWorker.kt', 'r') as f:
    content = f.read()

content = content.replace('fun doWork(): Result {', 'fun doWork(): Result {\n        android.util.Log.d("SyncWorker", "doWork() started")')
content = content.replace('if (pendingOps.isEmpty()) {', 'android.util.Log.d("SyncWorker", "Found \ pending operations")\n            if (pendingOps.isEmpty()) {')

with open('app/src/main/java/com/sgbdevapps/space360/data/sync/SyncWorker.kt', 'w') as f:
    f.write(content)

