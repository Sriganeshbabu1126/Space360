import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add import for QrCodeScanner icon
if "import androidx.compose.material.icons.filled.QrCodeScanner" not in content:
    content = content.replace("import androidx.compose.material.icons.filled.Add", "import androidx.compose.material.icons.filled.Add\nimport androidx.compose.material.icons.filled.QrCodeScanner")

# Change IssuesScreen signature
old_sig = """@Composable
fun IssuesScreen(
    navController: NavController,
    siteId: String,
    viewModel: IssueViewModel = hiltViewModel()
) {"""
new_sig = """@Composable
fun IssuesScreen(
    navController: NavController,
    siteId: String,
    onQRScanClick: () -> Unit = {},
    viewModel: IssueViewModel = hiltViewModel()
) {"""

if old_sig in content:
    content = content.replace(old_sig, new_sig)

# Find floatingActionButton in Scaffold
old_fab = """        floatingActionButton = {
            FloatingActionButton(
                onClick = { navController.navigate("create_issue") },
                containerColor = Color(0xFF2196F3)
            ) {
                Icon(Icons.Filled.Add, contentDescription = "Add Issue", tint = Color.White)
            }
        }"""
new_fab = """        floatingActionButton = {
            Column(horizontalAlignment = Alignment.End) {
                FloatingActionButton(
                    onClick = onQRScanClick,
                    containerColor = Color(0xFF1D9E75),
                    modifier = Modifier.padding(bottom = 16.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.QrCodeScanner,
                        contentDescription = "Scan QR Code",
                        tint = Color.White
                    )
                }
                FloatingActionButton(
                    onClick = { navController.navigate("create_issue") },
                    containerColor = Color(0xFF2196F3)
                ) {
                    Icon(Icons.Filled.Add, contentDescription = "Add Issue", tint = Color.White)
                }
            }
        }"""

if old_fab in content:
    content = content.replace(old_fab, new_fab)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
