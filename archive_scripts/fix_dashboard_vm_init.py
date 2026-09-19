import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/DashboardViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_init = """    init {
        loadDashboard()
    }

    private val _userRole = MutableStateFlow<String>("Contractor")
    val userRole: StateFlow<String> = _userRole"""
new_init = """    private val _userRole = MutableStateFlow<String>("Contractor")
    val userRole: StateFlow<String> = _userRole

    init {
        loadDashboard()
    }"""

if old_init in content:
    content = content.replace(old_init, new_init)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
