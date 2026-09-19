import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/DashboardViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_props = """    val dashboardState: StateFlow<DashboardState> = _dashboardState

    private val _selectedSite = MutableStateFlow<Site?>(null)
    val selectedSite: StateFlow<Site?> = _selectedSite

    fun selectSite(siteId: String) {
        _selectedSite.value = _sites.value.find { it.id == siteId }
    }
"""

if "val selectedSite: StateFlow<Site?>" not in content:
    content = content.replace("    val dashboardState: StateFlow<DashboardState> = _dashboardState", new_props)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
