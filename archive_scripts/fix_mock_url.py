import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/PathCaptureViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_url = """val currentFloorPlanUrl = MutableStateFlow<String?>("file:///android_asset/L1.jpg") // Mock URL for MVP"""
new_url = """val currentFloorPlanUrl = MutableStateFlow<String?>("https://images.unsplash.com/photo-1503387762-592deb58ef4e") // Mock URL for MVP"""

if old_url in content:
    content = content.replace(old_url, new_url)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
