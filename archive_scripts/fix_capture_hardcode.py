import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "val selectedSite by viewModel.selectedSite.collectAsState()" not in content:
    content = content.replace("val isLocationPinned by viewModel.isLocationPinned.collectAsState()", "val selectedSite by viewModel.selectedSite.collectAsState()\n    val isLocationPinned by viewModel.isLocationPinned.collectAsState()")

content = content.replace('viewModel.startRecording("SGB Test Construction Site")', 'viewModel.startRecording(selectedSite?.name ?: "Unknown Site")')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
