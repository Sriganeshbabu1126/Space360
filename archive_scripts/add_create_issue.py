import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/navigation/NavGraph.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import com.sgbdevapps.space360.presentation.screens.CreateIssueScreen" not in content:
    content = content.replace("import com.sgbdevapps.space360.presentation.screens.SettingsScreen", "import com.sgbdevapps.space360.presentation.screens.SettingsScreen\nimport com.sgbdevapps.space360.presentation.screens.CreateIssueScreen")

if "object CreateIssue : Route(\"create_issue\")" not in content:
    content = content.replace("object Settings : Route(\"settings\")", "object Settings : Route(\"settings\")\n    object CreateIssue : Route(\"create_issue\")")

if "composable(Route.CreateIssue.route)" not in content:
    content = content.replace("composable(Route.Settings.route) {\n            SettingsScreen()\n        }", "composable(Route.Settings.route) {\n            SettingsScreen()\n        }\n        composable(Route.CreateIssue.route) {\n            CreateIssueScreen(navController)\n        }")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
