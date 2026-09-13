import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/navigation/NavGraph.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure it imports ChangePasswordScreen
if "import com.sgbdevapps.space360.presentation.screens.ChangePasswordScreen" not in content:
    content = content.replace("import com.sgbdevapps.space360.presentation.screens.LoginScreen",
                              "import com.sgbdevapps.space360.presentation.screens.LoginScreen\nimport com.sgbdevapps.space360.presentation.screens.ChangePasswordScreen")

# Add change_password route
new_route = """        composable("change_password") {
            ChangePasswordScreen(
                onPasswordChanged = {
                    navController.navigate(Route.Dashboard.route) {
                        popUpTo(Route.Login.route) { inclusive = true }
                    }
                }
            )
        }
    }
}"""
content = content.replace("    }\n}", new_route)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
