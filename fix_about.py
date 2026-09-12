import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/SettingsScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

parts = content.split("@Composable\nfun AboutCard()")
before = parts[0]
after = parts[1]

# We need to find the end of AboutCard and replace it
# AboutCard looks like:
# {
#     Card(...) { ... }
# }
# Since it's the last function in the file, we can just replace everything after it.

new_about_card = """@Composable
fun AboutCard() {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp, 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                "Space360",
                style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Bold)
            )
            Text(
                "v1.0.0 Beta",
                style = MaterialTheme.typography.bodySmall
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                "360° Field Inspection for Construction Sites",
                style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray)
            )
            
            // NEW: Developer Information
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                "Developed by",
                style = MaterialTheme.typography.labelSmall.copy(
                    fontWeight = FontWeight.Bold,
                    color = Color.Gray
                )
            )
            
            Text(
                "Sriganesh Babu (SGB Dev Apps)",
                style = MaterialTheme.typography.bodySmall
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                "© 2026 Space360. All rights reserved.",
                style = MaterialTheme.typography.labelSmall.copy(color = Color.Gray)
            )
        }
    }
}
"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(before + new_about_card)
print("Done About card")
