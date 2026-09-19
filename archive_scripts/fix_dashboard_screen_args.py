import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/DashboardScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Fix ProjectDropdown invocation
old_inv = """                ProjectDropdown(
                    projects = sites,
                    selectedProject = selectedSite,
                    onProjectSelected = { viewModel.selectSite(it) },
                    userRole = userRole
                )"""
new_inv = """                ProjectDropdown(
                    projects = sites,
                    selectedProject = selectedSite,
                    onProjectSelected = { viewModel.selectSite(it) },
                    canCreateProject = canCreateProject
                )"""
if old_inv in content:
    content = content.replace(old_inv, new_inv)
else:
    # try another format if it's slightly different
    old_inv2 = """                ProjectDropdown(
                    projects = sites,
                    selectedProject = selectedSite,
                    onProjectSelected = { viewModel.selectSite(it) }
                )"""
    new_inv2 = """                ProjectDropdown(
                    projects = sites,
                    selectedProject = selectedSite,
                    onProjectSelected = { viewModel.selectSite(it) },
                    canCreateProject = canCreateProject
                )"""
    content = content.replace(old_inv2, new_inv2)


# Fix ProjectDropdown signature
old_sig = """fun ProjectDropdown(
    projects: List<Site>,
    selectedProject: Site?,
    onProjectSelected: (Site) -> Unit,
    userRole: String = "Contractor"
) {"""
new_sig = """fun ProjectDropdown(
    projects: List<Site>,
    selectedProject: Site?,
    onProjectSelected: (Site) -> Unit,
    canCreateProject: Boolean = false
) {"""
content = content.replace(old_sig, new_sig)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
