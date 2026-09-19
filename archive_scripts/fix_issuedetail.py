import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# I need to add state variables newStatus and hasChanges
# Currently the screen probably has:
#                 IssueStatusSelector(
#                     currentStatus = currentIssue.status,
#                     onStatusChange = { newStatus ->
#                         viewModel.updateIssueStatus(newStatus)
#                     }
#                 )

old_status_selector = """                // Issue Status Editable
                IssueStatusSelector(
                    currentStatus = currentIssue.status,
                    onStatusChange = { newStatus ->
                        viewModel.updateIssueStatus(newStatus)
                    }
                )"""

# I need to find where IssueDetailScreen is defined and inject newStatus and hasChanges
# It starts like:
# fun IssueDetailScreen(
#     navController: NavController,
#     issueId: String,
#     viewModel: IssueDetailViewModel = hiltViewModel()
# ) {
#     val issue by viewModel.issue.collectAsState()

old_vars = """    val issue by viewModel.issue.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()
    val context = LocalContext.current
    
    var photoUri by remember { mutableStateOf<Uri?>(null) }"""
    
new_vars = """    val issue by viewModel.issue.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()
    val context = LocalContext.current
    
    var newStatus by remember(issue?.status) { mutableStateOf(issue?.status ?: "Open") }
    var hasChanges by remember { mutableStateOf(false) }
    
    var photoUri by remember { mutableStateOf<Uri?>(null) }"""
    
content = content.replace(old_vars, new_vars)

new_status_selector = """                // Issue Status Editable
                IssueStatusSelector(
                    currentStatus = newStatus,
                    onStatusChange = { 
                        newStatus = it
                        hasChanges = (it != currentIssue.status)
                    }
                )
                
                // Apply Button
                if (hasChanges) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Button(
                        onClick = {
                            viewModel.updateIssueStatus(newStatus)
                            hasChanges = false
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF1D9E75)
                        )
                    ) {
                        Text("✓ Apply Status Change", color = Color.White)
                    }
                }"""
                
content = content.replace(old_status_selector, new_status_selector)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
