import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/DashboardScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Remove authViewModel from parameters
old_sig = """fun DashboardScreen(
    navController: NavController,
    viewModel: DashboardViewModel = hiltViewModel(),
    authViewModel: AuthViewModel = hiltViewModel()
) {"""
new_sig = """fun DashboardScreen(
    navController: NavController,
    onLogout: () -> Unit = {},
    viewModel: DashboardViewModel = hiltViewModel()
) {"""
content = content.replace(old_sig, new_sig)

# Add logoutComplete collection and LaunchedEffect
old_col = """    val dashboardState by viewModel.dashboardState.collectAsState()"""
new_col = """    val dashboardState by viewModel.dashboardState.collectAsState()
    val logoutComplete by viewModel.logoutComplete.collectAsState()

    LaunchedEffect(logoutComplete) {
        if (logoutComplete) {
            onLogout()
        }
    }"""
content = content.replace(old_col, new_col)

# Replace authViewModel.logout with viewModel.logout
old_btn = """IconButton(onClick = { authViewModel.logout() }) {"""
new_btn = """IconButton(onClick = { viewModel.logout() }) {"""
content = content.replace(old_btn, new_btn)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
