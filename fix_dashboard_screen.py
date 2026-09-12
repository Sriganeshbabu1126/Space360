import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/DashboardScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure we observe userRole
if "val userRole by viewModel.userRole.collectAsState()" not in content:
    content = content.replace("val selectedSite by viewModel.selectedSite.collectAsState()", "val selectedSite by viewModel.selectedSite.collectAsState()\n    val userRole by viewModel.userRole.collectAsState()")

# Update ProjectDropdown composable
old_dropdown_sig = """@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProjectDropdown(
    projects: List<Site>,
    selectedProject: Site?,
    onProjectSelected: (Site) -> Unit
) {"""

new_dropdown_sig = """@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProjectDropdown(
    projects: List<Site>,
    selectedProject: Site?,
    onProjectSelected: (Site) -> Unit,
    userRole: String = "Contractor"
) {"""
if old_dropdown_sig in content:
    content = content.replace(old_dropdown_sig, new_dropdown_sig)

old_dropdown_call = """        ProjectDropdown(
            projects = sites,
            selectedProject = selectedSite,
            onProjectSelected = { viewModel.selectSite(it.id) }
        )"""
new_dropdown_call = """        ProjectDropdown(
            projects = sites,
            selectedProject = selectedSite,
            onProjectSelected = { viewModel.selectSite(it.id) },
            userRole = userRole
        )"""
if old_dropdown_call in content:
    content = content.replace(old_dropdown_call, new_dropdown_call)

old_menu = """        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            projects.forEach { project ->
                DropdownMenuItem(
                    text = { Text(project.name) },
                    onClick = {
                        onProjectSelected(project)
                        expanded = false
                    }
                )
            }
        }"""
new_menu = """        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            projects.forEach { project ->
                DropdownMenuItem(
                    text = { Text(project.name) },
                    onClick = {
                        onProjectSelected(project)
                        expanded = false
                    }
                )
            }
            if (userRole == "Manager" || userRole == "Supervisor" || userRole == "360 Operator") {
                androidx.compose.material3.Divider()
                DropdownMenuItem(
                    text = { Text("➕ Create New Project", color = MaterialTheme.colorScheme.primary) },
                    onClick = {
                        // TODO: Navigate to create project screen
                        expanded = false
                    }
                )
            }
        }"""
if old_menu in content:
    content = content.replace(old_menu, new_menu)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
