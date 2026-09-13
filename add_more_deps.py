import os

filepath = "app/build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

missing_deps = """
    // CameraX
    val cameraxVersion = "1.3.4"
    implementation("androidx.camera:camera-core:$cameraxVersion")
    implementation("androidx.camera:camera-camera2:$cameraxVersion")
    implementation("androidx.camera:camera-lifecycle:$cameraxVersion")
    implementation("androidx.camera:camera-view:$cameraxVersion")
    
    // ML Kit Barcode Detection
    implementation("com.google.mlkit:barcode-scanning:17.2.0")
"""

content = content.replace(
    'implementation("androidx.hilt:hilt-work:1.2.0")',
    'implementation("androidx.hilt:hilt-work:1.2.0")' + missing_deps
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
