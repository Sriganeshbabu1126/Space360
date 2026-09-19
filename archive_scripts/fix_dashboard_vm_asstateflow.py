import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/DashboardViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import kotlinx.coroutines.flow.asStateFlow" not in content:
    content = content.replace("import kotlinx.coroutines.flow.StateFlow", "import kotlinx.coroutines.flow.StateFlow\nimport kotlinx.coroutines.flow.asStateFlow")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
