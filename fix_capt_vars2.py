import os
import re
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add the vars manually if they aren't there
if "val showLocationPicker by viewModel.showLocationPicker.collectAsState()" not in content:
    content = content.replace("    val cameraRecordingState by cameraViewModel.cameraRecordingState.collectAsState()", "    val cameraRecordingState by cameraViewModel.cameraRecordingState.collectAsState()\n    val showLocationPicker by viewModel.showLocationPicker.collectAsState()\n    val currentFloorPlanUrl by viewModel.currentFloorPlanUrl.collectAsState()\n    val pinnedLocation by viewModel.pinnedLocation.collectAsState()")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
