import os

filepath = "app/src/main/java/com/sgbdevapps/space360/service/OfflineSyncManager.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_func = """    private fun isNetworkAvailable(): Boolean {"""
new_func = """    suspend fun getPendingItemsForResource(resourceType: String, resourceId: String): List<OfflineSyncQueueEntity> {
        return db.offlineSyncQueueDao().getPendingItemsForResource(resourceType, resourceId)
    }

    private fun isNetworkAvailable(): Boolean {"""

if old_func in content:
    content = content.replace(old_func, new_func)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
