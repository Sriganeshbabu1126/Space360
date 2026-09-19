import os
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/SettingsScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace developer name
old_name = "Sriganesh Babu (SGB Dev Apps)"
new_name = "SGB Dev Apps"
if old_name in content:
    content = content.replace(old_name, new_name)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a5")
