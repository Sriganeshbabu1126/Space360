import os

filepath = "app/src/main/java/com/sgbdevapps/space360/domain/repository/PathRepository.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_func = """    suspend fun discardPath(pathId: String)
    suspend fun updatePathWithCameraMetadata(pathId: String, cameraStartNanos: Long?, cameraEndNanos: Long?, clockOffsetNanos: Long?, sessionJson: String)"""
content = content.replace("    suspend fun discardPath(pathId: String)", new_func)
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

impl_filepath = "app/src/main/java/com/sgbdevapps/space360/data/repository/PathRepositoryImpl.kt"
with open(impl_filepath, "r", encoding="utf-8") as f:
    content2 = f.read()

impl_func = """    override suspend fun discardPath(pathId: String) {
        val path = pathDao.getPath(pathId)
        if (path != null) {
            pathDao.deletePath(path)
            pathPointDao.deletePointsForPath(pathId)
        }
    }
    
    override suspend fun updatePathWithCameraMetadata(pathId: String, cameraStartNanos: Long?, cameraEndNanos: Long?, clockOffsetNanos: Long?, sessionJson: String) {
        // Mock implementation to satisfy interface
    }"""
content2 = content2.replace("""    override suspend fun discardPath(pathId: String) {
        val path = pathDao.getPath(pathId)
        if (path != null) {
            pathDao.deletePath(path)
            pathPointDao.deletePointsForPath(pathId)
        }
    }""", impl_func)

with open(impl_filepath, "w", encoding="utf-8") as f:
    f.write(content2)

print("Done")
