import os

filepath = "app/src/main/java/com/sgbdevapps/space360/service/OfflineSyncManager.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("syncQueueDao.insert(", "syncQueueDao.insertOperation(")
content = content.replace("syncQueueDao.getPendingItems(", "syncQueueDao.getPendingOperations(")
content = content.replace("syncQueueDao.update(", "syncQueueDao.updateOperation(")
content = content.replace("syncQueueDao.delete(", "syncQueueDao.deleteOperation(")

# wait, there's getPendingItemsForResource
old_func = """    suspend fun getPendingItemsForResource(resourceType: String, resourceId: String): List<SyncQueueEntity> {
        return syncQueueDao.getPendingItemsForResource(resourceType, resourceId)
    }"""
new_func = """    suspend fun getPendingItemsForResource(resourceType: String, resourceId: String): List<SyncQueueEntity> {
        return syncQueueDao.getPendingOperations().filter { it.resourceType == resourceType && it.resourceId == resourceId }
    }"""
content = content.replace(old_func, new_func)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
