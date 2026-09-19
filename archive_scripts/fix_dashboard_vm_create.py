import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/DashboardViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add missing imports for Flow mapping
if "import kotlinx.coroutines.flow.map" not in content:
    content = content.replace("import kotlinx.coroutines.flow.StateFlow", "import kotlinx.coroutines.flow.StateFlow\nimport kotlinx.coroutines.flow.map\nimport kotlinx.coroutines.flow.stateIn\nimport kotlinx.coroutines.flow.SharingStarted\nimport timber.log.Timber")

old_role = """    private val _userRole = MutableStateFlow<String>("Contractor")
    val userRole: StateFlow<String> = _userRole"""
new_role = """    private val _userRole = MutableStateFlow<String>("Manager")
    val userRole: StateFlow<String> = _userRole

    val canCreateProject: StateFlow<Boolean> = _userRole.map { role ->
        val roleStr = role.lowercase().trim()
        Timber.d("ROLE_DEBUG: normalised role = '$roleStr'")
        roleStr in listOf("manager", "supervisor", "360 operator", "360operator", "admin")
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), false)"""
if old_role in content:
    content = content.replace(old_role, new_role)
else:
    print("Could not find old_role block!")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
