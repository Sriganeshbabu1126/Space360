
with open('app/src/main/java/com/sgbdevapps/space360/data/repository/PathRepositoryImpl.kt', 'r') as f:
    content = f.read()

content = content.replace(
    'import javax.inject.Inject',
    'import android.content.Context\nimport dagger.hilt.android.qualifiers.ApplicationContext\nimport javax.inject.Inject'
)

content = content.replace(
    'private val syncQueueDao: SyncQueueDao\n) : PathRepository',
    'private val syncQueueDao: SyncQueueDao,\n    @ApplicationContext private val context: Context\n) : PathRepository'
)

content = content.replace(
    'syncQueueDao.insertOperation(syncOp)\n    }',
    'syncQueueDao.insertOperation(syncOp)\n        com.sgbdevapps.space360.data.sync.SyncWorker.triggerImmediateSyncOnConnectivity(context)\n    }'
)

with open('app/src/main/java/com/sgbdevapps/space360/data/repository/PathRepositoryImpl.kt', 'w') as f:
    f.write(content)

