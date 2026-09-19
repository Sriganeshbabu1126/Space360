import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/repository/AuthRepositoryImpl.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('role = "Contractor"', 'role = "Manager"')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
