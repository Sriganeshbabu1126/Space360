import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/remote/ApiService.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('@Path("issueId") issueId: String', '@Path("id") issueId: String')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
