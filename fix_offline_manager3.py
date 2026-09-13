import os

filepath = "app/src/main/java/com/sgbdevapps/space360/service/OfflineSyncManager.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace import
content = content.replace("import com.sgbdevapps.space360.data.local.OfflineSyncQueueEntity", "import com.sgbdevapps.space360.data.local.SyncQueueEntity")

# Replace queueItem creation
old_create = """        val queueItem = OfflineSyncQueueEntity(
            action = action,
            resourceType = resourceType,
            resourceId = resourceId,
            payload = jsonPayload
        )"""
new_create = """        val queueItem = SyncQueueEntity(
            operationType = action,
            issueId = resourceId,
            payload = jsonPayload,
            createdAt = System.currentTimeMillis(),
            status = "PENDING"
        )"""
content = content.replace(old_create, new_create)

# Replace usage in syncPendingItems
content = content.replace("item.action", "item.operationType")
content = content.replace("item.resourceId", "item.issueId")

old_update_success = """                item.copy(
                    status = "synced",
                    updatedAt = System.currentTimeMillis()
                ).let { db.syncQueueDao().updateOperation(it) }"""
new_update_success = """                item.copy(
                    status = "SYNCED",
                    syncedAt = System.currentTimeMillis()
                ).let { db.syncQueueDao().updateOperation(it) }"""
content = content.replace(old_update_success, new_update_success)

old_update_fail = """                item.copy(
                    status = if (item.attempts >= item.maxAttempts) "failed" else "pending",
                    attempts = item.attempts + 1,
                    lastAttemptAt = System.currentTimeMillis(),
                    errorMessage = e.message,
                    updatedAt = System.currentTimeMillis()
                ).let { db.syncQueueDao().updateOperation(it) }"""
new_update_fail = """                item.copy(
                    status = if (item.retryCount >= item.maxRetries) "FAILED" else "PENDING",
                    retryCount = item.retryCount + 1,
                    lastErrorAt = System.currentTimeMillis(),
                    lastError = e.message
                ).let { db.syncQueueDao().updateOperation(it) }"""
content = content.replace(old_update_fail, new_update_fail)

# Replace getPendingItemsForResource
old_func = """    suspend fun getPendingItemsForResource(resourceType: String, resourceId: String): List<OfflineSyncQueueEntity> {
        return db.syncQueueDao().getPendingOperations().filter { it.resourceType == resourceType && it.resourceId == resourceId }
    }"""
new_func = """    suspend fun getPendingItemsForResource(resourceType: String, resourceId: String): List<SyncQueueEntity> {
        return db.syncQueueDao().getPendingOperations().filter { it.issueId == resourceId }
    }"""
content = content.replace(old_func, new_func)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
