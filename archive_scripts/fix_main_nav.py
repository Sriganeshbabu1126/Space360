import os

filepath = "app/src/main/java/com/sgbdevapps/space360/MainActivity.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Import
if "import com.sgbdevapps.space360.presentation.viewmodels.MainViewModel" not in content:
    content = content.replace("import com.sgbdevapps.space360.presentation.viewmodels.AuthViewModel", "import com.sgbdevapps.space360.presentation.viewmodels.AuthViewModel\nimport com.sgbdevapps.space360.presentation.viewmodels.MainViewModel\nimport android.widget.Toast\nimport androidx.compose.ui.platform.LocalContext\nimport androidx.compose.ui.graphics.Color")

old_mainapp = """@Composable
fun MainApp(
    viewModel: AuthViewModel = hiltViewModel(),
    settingsViewModel: SettingsViewModel = hiltViewModel()
) {"""
new_mainapp = """@Composable
fun MainApp(
    viewModel: AuthViewModel = hiltViewModel(),
    settingsViewModel: SettingsViewModel = hiltViewModel(),
    mainViewModel: MainViewModel = hiltViewModel()
) {"""
content = content.replace(old_mainapp, new_mainapp)

old_bottombar_call = "BottomNavigationBar(navController)"
new_bottombar_call = """val selectedSite by mainViewModel.selectedSite.collectAsState()
                BottomNavigationBar(navController, selectedSite != null)"""
if old_bottombar_call in content:
    content = content.replace(old_bottombar_call, new_bottombar_call)

old_bottombar_sig = """@Composable
fun BottomNavigationBar(navController: NavHostController) {"""
new_bottombar_sig = """@Composable
fun BottomNavigationBar(navController: NavHostController, isProjectSelected: Boolean) {"""
if old_bottombar_sig in content:
    content = content.replace(old_bottombar_sig, new_bottombar_sig)

old_bottombar_content = """        NavigationBarItem(
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
        )"""

new_bottombar_content = """        val context = LocalContext.current
        NavigationBarItem(
            icon = { Icon(Icons.AutoMirrored.Filled.List, contentDescription = "Issues", tint = if (isProjectSelected) MaterialTheme.colorScheme.onSurface else Color.Gray) },
            label = { Text("Issues", color = if (isProjectSelected) MaterialTheme.colorScheme.onSurface else Color.Gray) },
            selected = currentRoute?.startsWith("issues") == true,
            onClick = {
                if (isProjectSelected) {
                    navController.navigate(Route.IssuesList.route.replace("{siteId}", "all"))
                } else {
                    Toast.makeText(context, "Please select a project first", Toast.LENGTH_SHORT).show()
                }
            }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Add, contentDescription = "Capture", tint = if (isProjectSelected) MaterialTheme.colorScheme.onSurface else Color.Gray) },
            label = { Text("Capture", color = if (isProjectSelected) MaterialTheme.colorScheme.onSurface else Color.Gray) },
            selected = currentRoute == Route.Capture.route,
            onClick = {
                if (isProjectSelected) {
                    navController.navigate(Route.Capture.route)
                } else {
                    Toast.makeText(context, "Please select a project first", Toast.LENGTH_SHORT).show()
                }
            }
        )"""
if old_bottombar_content in content:
    content = content.replace(old_bottombar_content, new_bottombar_content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
