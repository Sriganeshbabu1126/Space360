import re

filepath = 'F:/Space360/app/src/main/java/com/sgbdevapps/space360/data/repository/IssueRepositoryImpl.kt'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'type = response\.type,',
    r'type = response.type ?: "defect",',
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
