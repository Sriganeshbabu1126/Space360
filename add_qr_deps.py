import os

filepath = "app/build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

deps = """
    // ML Kit Barcode Detection
    implementation("com.google.mlkit:barcode-scanning:17.2.0")
    
    // CameraX
    val cameraxVersion = "1.3.4"
    implementation("androidx.camera:camera-core:$cameraxVersion")
    implementation("androidx.camera:camera-camera2:$cameraxVersion")
    implementation("androidx.camera:camera-lifecycle:$cameraxVersion")
    implementation("androidx.camera:camera-view:$cameraxVersion")
    
    // Accompanist Permissions
    implementation("com.google.accompanist:accompanist-permissions:0.35.1-alpha")
"""

if "mlkit:barcode-scanning" not in content:
    content = content.replace('implementation("io.coil-kt:coil-compose:2.4.0")', 'implementation("io.coil-kt:coil-compose:2.4.0")\n' + deps)
    
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
