import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/DashboardScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_menu = """            val roleStr = userRole.lowercase().trim()
            val canCreateProject = roleStr in listOf("manager", "supervisor", "360 operator")
            if (canCreateProject) {
                androidx.compose.material3.Divider()
                DropdownMenuItem(
                    text = { Text("? Create New Project", color = MaterialTheme.colorScheme.primary) },
                    onClick = {
                        // TODO: Navigate to create project screen
                        expanded = false
                    }
                )
            }"""
new_menu = """            val roleStr = userRole.lowercase().trim()
            val canCreateProject = roleStr in listOf("manager", "supervisor", "360 operator")
            if (canCreateProject) {
                HorizontalDivider()
                DropdownMenuItem(
                    text = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Default.AddCircleOutline,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                "Create New Project",
                                color = MaterialTheme.colorScheme.primary,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    },
                    onClick = {
                        // TODO: Navigate to create project screen
                        expanded = false
                    }
                )
            }"""
if old_menu in content:
    content = content.replace(old_menu, new_menu)
else:
    print("Could not find the dropdown menu code block again!")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
