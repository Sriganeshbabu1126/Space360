import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_status = """                    Text(
                        "Insta Recording Status",
                        style = MaterialTheme.typography.titleMedium.copy(
                            color = Color.Gray,
                            fontWeight = FontWeight.SemiBold
                        )
                    )"""

new_status = """                    Text(
                        "🎥 Insta360 Recording Status: ACTIVE",
                        style = MaterialTheme.typography.titleMedium.copy(
                            color = Color.Gray,
                            fontWeight = FontWeight.SemiBold
                        )
                    )"""

if old_status in content:
    content = content.replace(old_status, new_status)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
