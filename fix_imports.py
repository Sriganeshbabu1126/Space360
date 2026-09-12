import os
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/SettingsScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import androidx.compose.runtime.getValue", "import androidx.compose.runtime.getValue\nimport androidx.compose.runtime.mutableStateOf\nimport androidx.compose.runtime.remember\nimport androidx.compose.runtime.setValue")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
