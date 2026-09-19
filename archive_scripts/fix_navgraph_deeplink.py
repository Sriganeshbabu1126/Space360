import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/navigation/NavGraph.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import androidx.navigation.navDeepLink" not in content:
    content = content.replace("import androidx.navigation.compose.composable", "import androidx.navigation.compose.composable\nimport androidx.navigation.navDeepLink")

old_route = """        composable(Route.IssueDetail.route) { backStackEntry ->
            val issueId = backStackEntry.arguments?.getString("issueId") ?: ""
            IssueDetailScreen(navController, issueId)
        }"""
new_route = """        composable(
            route = Route.IssueDetail.route,
            deepLinks = listOf(navDeepLink { uriPattern = "space360://issue/{issueId}" })
        ) { backStackEntry ->
            val issueId = backStackEntry.arguments?.getString("issueId") ?: ""
            IssueDetailScreen(navController, issueId)
        }"""
if old_route in content:
    content = content.replace(old_route, new_route)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
