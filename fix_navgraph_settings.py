import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/navigation/NavGraph.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_settings = """        composable(Route.Settings.route) {
            SettingsScreen()
        }"""
new_settings = """        composable(Route.Settings.route) {
            SettingsScreen(
                onLogout = {
                    navController.navigate(Route.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }"""
if old_settings in content:
    content = content.replace(old_settings, new_settings)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
