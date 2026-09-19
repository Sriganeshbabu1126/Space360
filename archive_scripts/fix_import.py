import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/repository/UserManagementRepository.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import com.sgbdevapps.space360.data.remote.NotifyUserRequest" not in content:
    content = content.replace("import com.sgbdevapps.space360.data.remote.ApiService", "import com.sgbdevapps.space360.data.remote.ApiService\nimport com.sgbdevapps.space360.data.remote.NotifyUserRequest")
    
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
