import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/LoginScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_state = """    val authState by viewModel.authState.collectAsState()

    LaunchedEffect(authState) {
        if (authState is AuthViewModel.AuthState.Success) {
            navController.navigate(Route.Dashboard.route) {
                popUpTo(Route.Login.route) { inclusive = true }
            }
        }
    }"""
new_state = """    val authState by viewModel.authState.collectAsState()
    val mustChangePassword by viewModel.mustChangePassword.collectAsState()

    LaunchedEffect(authState) {
        if (authState is AuthViewModel.AuthState.Success) {
            navController.navigate(Route.Dashboard.route) {
                popUpTo(Route.Login.route) { inclusive = true }
            }
        }
    }

    LaunchedEffect(mustChangePassword) {
        if (mustChangePassword) {
            navController.navigate("change_password")
        }
    }"""
content = content.replace(old_state, new_state)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
