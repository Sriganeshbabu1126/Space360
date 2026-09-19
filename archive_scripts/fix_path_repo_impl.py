import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/repository/PathRepositoryImpl.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_impl = """
    override suspend fun updatePathWithCameraMetadata(
        pathId: String,
        cameraStartNanos: Long?,
        cameraEndNanos: Long?,
        clockOffsetNanos: Long?,
        sessionJson: String
    ) {
        // Mock implementation
    }
}"""
content = content[:content.rfind("}")] + new_impl

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
