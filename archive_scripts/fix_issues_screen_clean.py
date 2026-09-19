import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace top part
old_content = """    LaunchedEffect(siteId) {
        if (siteId != "all" && siteId.isNotEmpty()) {
            viewModel.selectSite(siteId)
        }
    }

    if (selectedSite == null) {
        // Show project dropdown if no project selected
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("Select Project") },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.primary, titleContentColor = Color.White)
                )
            }
        ) { innerPadding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(16.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("Select a project to view issues", style = MaterialTheme.typography.bodyLarge)
                Spacer(modifier = Modifier.height(16.dp))
                
                val sites by viewModel.sites.collectAsState()
                ProjectDropdown(
                    projects = sites,
                    selectedProject = null,
                    onProjectSelected = { site ->
                        viewModel.selectSite(site.id)
                    }
                )
            }
        }
    } else {
        // Show issues for selected site
        Scaffold("""

new_content = """    // Inherits selectedSite from SessionManager automatically via IssueViewModel init

    if (selectedSite != null) {
        // Show issues for selected site
        Scaffold("""

if old_content in content:
    content = content.replace(old_content, new_content)
    
# Remove one closing brace at the end
content = content.rsplit("}", 1)[0]

# Fix ?? to emoji
content = content.replace("?? ${it.name}", "🏢 ${it.name}")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
