import os
import re

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/DashboardScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r"if \(canCreateProject\) \{[\s\S]*?onClick = \{[\s\S]*?expanded = false\s*\}\s*\)\s*\}"

new_menu = """if (canCreateProject) {
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

match = re.search(pattern, content)
if match:
    content = content.replace(match.group(0), new_menu)
else:
    print("Regex could not match")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
