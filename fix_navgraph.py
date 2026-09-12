import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/navigation/NavGraph.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_dash = """        composable(Route.Dashboard.route) {
            DashboardScreen(navController)
        }"""
new_dash = """        composable(Route.Dashboard.route) {
            DashboardScreen(
                navController = navController,
                onLogout = {
                    navController.navigate(Route.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }"""
if old_dash in content:
    content = content.replace(old_dash, new_dash)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
