import os

# 1. Fix OfflineSyncManager
filepath = "app/src/main/java/com/sgbdevapps/space360/service/OfflineSyncManager.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("db.syncQueueDao().insert(", "db.syncQueueDao().insertOperation(")
content = content.replace("db.syncQueueDao().getPendingItems()", "db.syncQueueDao().getPendingOperations()")
content = content.replace("db.syncQueueDao().update(", "db.syncQueueDao().updateOperation(")
content = content.replace("db.syncQueueDao().delete(item.id)", "db.syncQueueDao().deleteOperation(item)")
content = content.replace("db.syncQueueDao().getPendingItemsForResource(resourceType, resourceId)", "db.syncQueueDao().getPendingOperations().filter { it.resourceType == resourceType && it.resourceId == resourceId }")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)


# 2. Fix Space360App.kt
filepath = "app/src/main/java/com/sgbdevapps/space360/Space360App.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("override fun getWorkManagerConfiguration()", "override val workManagerConfiguration: Configuration\n        get()")
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# 3. Fix PathRepositoryImpl.kt
filepath = "app/src/main/java/com/sgbdevapps/space360/data/repository/PathRepositoryImpl.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_impl = """    override suspend fun updatePathWithCameraMetadata(
        pathId: String,
        cameraStartNanos: Long?,
        cameraEndNanos: Long?,
        clockOffsetNanos: Long?,
        sessionJson: String
    ) {
        // Mock implementation
    }"""
content = content.replace("    override suspend fun updatePathWithCameraMetadata(pathId: String, cameraStartNanos: Long?, cameraEndNanos: Long?, clockOffsetNanos: Long?, sessionJson: String) {\n        // Mock implementation to satisfy interface\n    }", new_impl)
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# 4. Fix ApiService.kt
filepath = "app/src/main/java/com/sgbdevapps/space360/data/remote/ApiService.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "notifyNewUser" not in content:
    new_auth = """    @GET("auth/verify")
    suspend fun verifyToken(): retrofit2.Response<Unit>
    
    @POST("admin/notify-new-user")
    suspend fun notifyNewUser(@Body request: com.sgbdevapps.space360.data.remote.NotifyUserRequest): retrofit2.Response<Unit>"""
    content = content.replace('    @GET("auth/verify")\n    suspend fun verifyToken(): retrofit2.Response<Unit>', new_auth)
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# 5. Add NotifyUserRequest to ApiModels.kt
filepath = "app/src/main/java/com/sgbdevapps/space360/data/remote/ApiModels.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "NotifyUserRequest" not in content:
    content += "\n@kotlinx.serialization.Serializable\ndata class NotifyUserRequest(\n    val email: String,\n    val name: String,\n    val temp_password: String\n)\n"
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
