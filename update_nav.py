import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/navigation/NavGraph.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import com.sgbdevapps.space360.presentation.screens.SettingsScreen" not in content:
    content = content.replace("import com.sgbdevapps.space360.presentation.screens.ProfileScreen", "import com.sgbdevapps.space360.presentation.screens.ProfileScreen\nimport com.sgbdevapps.space360.presentation.screens.SettingsScreen")

if "object Settings : Route(\"settings\")" not in content:
    content = content.replace("object Profile : Route(\"profile\")", "object Profile : Route(\"profile\")\n    object Settings : Route(\"settings\")")

if "composable(Route.Settings.route)" not in content:
    content = content.replace("composable(Route.Profile.route) {\n            ProfileScreen(navController)\n        }", "composable(Route.Profile.route) {\n            ProfileScreen(navController)\n        }\n        composable(Route.Settings.route) {\n            SettingsScreen()\n        }")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done NavGraph")

# Now MainActivity
filepath = "app/src/main/java/com/sgbdevapps/space360/MainActivity.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import com.sgbdevapps.space360.presentation.viewmodels.SettingsViewModel" not in content:
    content = content.replace("import com.sgbdevapps.space360.presentation.viewmodels.AuthViewModel", "import com.sgbdevapps.space360.presentation.viewmodels.AuthViewModel\nimport com.sgbdevapps.space360.presentation.viewmodels.SettingsViewModel")

# Fix theme import
if "import com.sgbdevapps.space360.ui.theme.Space360Theme" in content:
    content = content.replace("import com.sgbdevapps.space360.ui.theme.Space360Theme", "import com.sgbdevapps.space360.presentation.theme.Space360Theme")

# Add SettingsViewModel to MainApp
if "viewModel: AuthViewModel = hiltViewModel()" in content and "settingsViewModel: SettingsViewModel" not in content:
    content = content.replace(
        "fun MainApp(\n    viewModel: AuthViewModel = hiltViewModel()\n)",
        "fun MainApp(\n    viewModel: AuthViewModel = hiltViewModel(),\n    settingsViewModel: SettingsViewModel = hiltViewModel()\n)"
    )

# Use color scheme
if "val isLoggedIn by viewModel.isLoggedIn.collectAsState()" in content and "selectedColorScheme" not in content:
    content = content.replace(
        "val isLoggedIn by viewModel.isLoggedIn.collectAsState()",
        "val isLoggedIn by viewModel.isLoggedIn.collectAsState()\n    val selectedColorScheme by settingsViewModel.colorScheme.collectAsState()"
    )

if "Space360Theme {" in content:
    content = content.replace("Space360Theme {", "Space360Theme(colorScheme = selectedColorScheme) {")

# Update Bottom Navigation
bottom_nav = """
@Composable
fun BottomNavigationBar(navController: NavHostController) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route
    
    NavigationBar(modifier = Modifier.fillMaxWidth()) {
        NavigationBarItem(
            icon = { Icon(Icons.Default.Home, contentDescription = "Dashboard") },
            label = { Text("Dashboard") },
            selected = currentRoute == Route.Dashboard.route,
            onClick = { navController.navigate(Route.Dashboard.route) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.List, contentDescription = "Issues") },
            label = { Text("Issues") },
            selected = currentRoute?.startsWith("issues") == true,
            onClick = { navController.navigate(Route.IssuesList.route.replace("{siteId}", "all")) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Add, contentDescription = "Capture") },
            label = { Text("Capture") },
            selected = currentRoute == Route.Capture.route,
            onClick = { navController.navigate(Route.Capture.route) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
            label = { Text("Settings") },
            selected = currentRoute == Route.Settings.route,
            onClick = { navController.navigate(Route.Settings.route) }
        )
    }
}
"""

import re
content = re.sub(r'@Composable\s*fun BottomNavigationBar.*?}\s*}', bottom_nav.strip(), content, flags=re.DOTALL)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done MainActivity")

