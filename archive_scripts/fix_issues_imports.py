import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import androidx.compose.foundation.BorderStroke", "import androidx.compose.foundation.BorderStroke\nimport androidx.compose.foundation.background")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
