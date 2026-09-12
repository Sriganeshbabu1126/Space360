import os

filepath = "app/src/main/java/com/sgbdevapps/space360/MainActivity.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("Icons.AutoMirrored.Filled.List", "Icons.Default.List")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
