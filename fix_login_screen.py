import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/auth/LoginScreen.kt"
if not os.path.exists(filepath):
    filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/LoginScreen.kt"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_state = """    val isLoggedIn by viewModel.isLoggedIn.collectAsState()"""
new_state = """    val isLoggedIn by viewModel.isLoggedIn.collectAsState()
    val mustChangePassword by viewModel.mustChangePassword.collectAsState()

    LaunchedEffect(mustChangePassword) {
        if (mustChangePassword) {
            navController.navigate("change_password")
        }
    }"""
if old_state in content:
    content = content.replace(old_state, new_state)
else:
    print("Could not find isLoggedIn collect")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
