import re

filepath = 'F:/Space360/app/src/main/java/com/sgbdevapps/space360/data/repository/IssueRepositoryImpl.kt'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace assignments
content = re.sub(
    r'description = response\.description,',
    r'description = response.description ?: "",',
    content
)
content = re.sub(
    r'priority = response\.priority,',
    r'priority = response.priority ?: "Medium",',
    content
)
content = re.sub(
    r'assignedTo = response\.assigned_to,',
    r'assignedTo = response.assigned_to ?: "",',
    content
)
content = re.sub(
    r'assignedToName = response\.assigned_to_name,',
    r'assignedToName = response.assigned_to_name ?: "Unassigned",',
    content
)
content = re.sub(
    r'comments = response\.comments\.map \{ IssueComment\(it\.id, it\.issue_id, it\.user_id, it\.user_name, it\.text, it\.created_at\) \},',
    r'comments = response.comments?.map { IssueComment(it.id, it.issue_id, it.user_id, it.user_name, it.text, it.created_at) } ?: emptyList(),',
    content
)
content = re.sub(
    r'photos = response\.photos\.map \{ IssuePhoto\(it\.id, it\.issue_id, it\.photo_url, it\.uploaded_at\) \}',
    r'photos = response.photos?.map { IssuePhoto(it.id, it.issue_id, it.photo_url, it.uploaded_at) } ?: emptyList()',
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
