import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

replacement = """    LaunchedEffect(siteId) {
        if (siteId != "all") {
            viewModel.selectSite(siteId)
        }
    }

    if (selectedSite == null) {
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
        Scaffold("""

content = content.replace("    LaunchedEffect(siteId) {\n        viewModel.loadIssues(siteId)\n    }\n\n    Scaffold(", replacement)

# ensure we add a closing brace for the else block!
content = content + "\n}"

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
