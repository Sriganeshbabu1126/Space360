import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_fab = """            FloatingActionButton(
                onClick = { /* Navigate to create issue */ },
                containerColor = Color(0xFF1D9E75),
                shape = RoundedCornerShape(16.dp)
            ) {
                Icon(Icons.Filled.Add, contentDescription = "Add Issue", tint = Color.White)
            }"""
new_fab = """            FloatingActionButton(
                onClick = { 
                    navController.navigate("create_issue")
                },
                containerColor = MaterialTheme.colorScheme.primary,
                shape = RoundedCornerShape(16.dp)
            ) {
                Icon(Icons.Filled.Add, contentDescription = "Add Issue", tint = Color.White)
            }"""
content = content.replace(old_fab, new_fab)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
