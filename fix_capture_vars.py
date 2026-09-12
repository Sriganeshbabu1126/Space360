import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old = "    val elapsedTime by viewModel.elapsedTimeSeconds.collectAsState()"
new = "    val elapsedTime by viewModel.elapsedTimeSeconds.collectAsState()\n    val isLocationPinned by viewModel.isLocationPinned.collectAsState()"
content = content.replace(old, new)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
