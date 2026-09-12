import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("url = it.file_url", "url = it.photo_url")
content = content.replace("createdAt = it.created_at", "createdAt = it.uploaded_at ?: \"\"")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done mapping fix")
