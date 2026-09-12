import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/DashboardScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_if = """            if (userRole == "Manager" || userRole == "Supervisor" || userRole == "360 Operator") {"""
new_if = """            val roleStr = userRole.lowercase().trim()
            val canCreateProject = roleStr in listOf("manager", "supervisor", "360 operator")
            if (canCreateProject) {"""

if old_if in content:
    content = content.replace(old_if, new_if)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
