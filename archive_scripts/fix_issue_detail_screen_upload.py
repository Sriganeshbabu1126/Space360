import os
import re

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace all occurrences of uploadPhotoUri(it) with addPhotoToIssue(issueId, it)
content = re.sub(r'viewModel\.uploadPhotoUri\((.*?)\)', r'viewModel.addPhotoToIssue(issueId, \1)', content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
