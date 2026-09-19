import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/navigation/NavGraph.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# import QRScannerScreen
if "import com.sgbdevapps.space360.presentation.screens.QRScannerScreen" not in content:
    content = content.replace("import com.sgbdevapps.space360.presentation.screens.SettingsScreen", "import com.sgbdevapps.space360.presentation.screens.SettingsScreen\nimport com.sgbdevapps.space360.presentation.screens.QRScannerScreen")

# Add route
if "object QRScanner : Route(\"qr_scanner\")" not in content:
    content = content.replace('object CreateIssue : Route("create_issue")', 'object CreateIssue : Route("create_issue")\n    object QRScanner : Route("qr_scanner")')

# Change IssuesScreen call
old_issues = """        composable(Route.IssuesList.route) { backStackEntry ->
            val siteId = backStackEntry.arguments?.getString("siteId") ?: ""
            IssuesScreen(navController, siteId)
        }"""
new_issues = """        composable(Route.IssuesList.route) { backStackEntry ->
            val siteId = backStackEntry.arguments?.getString("siteId") ?: ""
            IssuesScreen(
                navController = navController,
                siteId = siteId,
                onQRScanClick = {
                    navController.navigate(Route.QRScanner.route)
                }
            )
        }"""
if old_issues in content:
    content = content.replace(old_issues, new_issues)

# Add QRScanner composable
qr_route = """        composable(Route.QRScanner.route) {
            QRScannerScreen(
                onQRScanned = { issueId ->
                    navController.navigate("issue/$issueId") {
                        popUpTo(Route.QRScanner.route) { inclusive = true }
                    }
                },
                onBackClick = {
                    navController.popBackStack()
                }
            )
        }"""
if qr_route not in content:
    content = content.replace("    }\n}", f"{qr_route}\n    }}\n}}")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
