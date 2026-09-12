import os

filepath = "app/src/main/java/com/sgbdevapps/space360/MainActivity.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Revert Space360Theme in onCreate
content = content.replace("Space360Theme(colorScheme = selectedColorScheme) {", "Space360Theme {", 1)

# Add Space360Theme around NavGraph in MainApp
old_scaffold = "Scaffold(\n        bottomBar = {"
new_scaffold = "Space360Theme(colorScheme = selectedColorScheme) {\n    Scaffold(\n        bottomBar = {"

content = content.replace(old_scaffold, new_scaffold)
content = content.replace("NavGraph(navController, isLoggedIn)\n        }\n    }", "NavGraph(navController, isLoggedIn)\n        }\n    }\n    }")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
