import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/DashboardScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_col = """    val dashboardState by viewModel.dashboardState.collectAsState()
    val logoutComplete by viewModel.logoutComplete.collectAsState()"""
new_col = """    val dashboardState by viewModel.dashboardState.collectAsState()
    val logoutComplete by viewModel.logoutComplete.collectAsState()
    val canCreateProject by viewModel.canCreateProject.collectAsState()"""
if old_col in content:
    content = content.replace(old_col, new_col)

old_menu = """            val roleStr = userRole.lowercase().trim()
            val canCreateProject = roleStr in listOf("manager", "supervisor", "360 operator")
            if (canCreateProject) {"""
new_menu = """            if (canCreateProject) {"""
if old_menu in content:
    content = content.replace(old_menu, new_menu)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
