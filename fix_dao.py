import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/local/OfflineSyncQueueDao.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_dao = """    @Query("SELECT * FROM offline_sync_queue WHERE status = 'pending' ORDER BY createdAt ASC LIMIT 50")
    suspend fun getPendingItems(): List<OfflineSyncQueueEntity>"""
new_dao = """    @Query("SELECT * FROM offline_sync_queue WHERE status = 'pending' ORDER BY createdAt ASC LIMIT 50")
    suspend fun getPendingItems(): List<OfflineSyncQueueEntity>
    
    @Query("SELECT * FROM offline_sync_queue WHERE status = 'pending' AND resourceType = :resourceType AND resourceId = :resourceId ORDER BY createdAt ASC")
    suspend fun getPendingItemsForResource(resourceType: String, resourceId: String): List<OfflineSyncQueueEntity>"""

if old_dao in content:
    content = content.replace(old_dao, new_dao)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
