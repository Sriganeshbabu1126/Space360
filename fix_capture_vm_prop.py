import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/PathCaptureViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_prop = """    private val _isLocationPinned = MutableStateFlow(false)"""
new_prop = """    val selectedSite = sessionManager.selectedSite

    private val _isLocationPinned = MutableStateFlow(false)"""
if old_prop in content:
    content = content.replace(old_prop, new_prop)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
