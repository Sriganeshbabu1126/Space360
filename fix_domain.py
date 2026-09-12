import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Fix Comments mapping
old_comment = """                    com.sgbdevapps.space360.domain.model.IssueComment(
                        id = it.id,
                        text = it.text,
                        authorName = it.user_name,
                        createdAt = it.created_at
                    )"""
new_comment = """                    com.sgbdevapps.space360.domain.model.IssueComment(
                        id = it.id,
                        issueId = issueId,
                        userId = "unknown",
                        userName = it.user_name,
                        text = it.text,
                        createdAt = it.created_at
                    )"""
content = content.replace(old_comment, new_comment)

# Fix offline comment mapping
old_offline = """                    com.sgbdevapps.space360.domain.model.IssueComment(
                        id = "temp_${System.currentTimeMillis()}",
                        text = text,
                        authorName = "You (Offline)",
                        createdAt = "Just now"
                    )"""
new_offline = """                    com.sgbdevapps.space360.domain.model.IssueComment(
                        id = "temp_${System.currentTimeMillis()}",
                        issueId = issueId,
                        userId = "current_user",
                        userName = "You (Offline)",
                        text = text,
                        createdAt = "Just now"
                    )"""
content = content.replace(old_offline, new_offline)

# Fix Photos mapping
old_photo = """                    com.sgbdevapps.space360.domain.model.IssuePhoto(
                        id = it.id,
                        url = it.photo_url,
                        createdAt = it.uploaded_at ?: ""
                    )"""
new_photo = """                    com.sgbdevapps.space360.domain.model.IssuePhoto(
                        id = it.id,
                        issueId = issueId,
                        photoUrl = it.photo_url,
                        uploadedAt = it.uploaded_at ?: ""
                    )"""
content = content.replace(old_photo, new_photo)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)


filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("photo.url", "photo.photoUrl")
content = content.replace("comment.authorName", "comment.userName")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
