import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/PathCaptureViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Remove old currentFloorPlanUrl
old_url = """    val currentFloorPlanUrl = MutableStateFlow<String?>("https://images.unsplash.com/photo-1503387762-592deb58ef4e") // Mock URL for MVP"""
new_url = """    private val _floorPlanLoadState = MutableStateFlow<com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState>(com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loading)
    val floorPlanLoadState: StateFlow<com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState> = _floorPlanLoadState"""

if old_url in content:
    content = content.replace(old_url, new_url)

old_init = """    init {
        // Mock points"""
new_init = """    init {
        loadFloorPlan()
        // Mock points"""
if old_init in content:
    content = content.replace(old_init, new_init)

# Add loadFloorPlan method
load_method = """
    private fun loadFloorPlan() {
        viewModelScope.launch {
            try {
                _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loading

                val site = sessionManager.selectedSite.value
                if (site == null) {
                    _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.NoProject
                    return@launch
                }

                val url = site.floorPlanUrl
                if (!url.isNullOrBlank()) {
                    _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loaded(url)
                } else {
                    _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.NoFloorPlan
                }
            } catch (e: Exception) {
                _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Error(e.message ?: "Unknown error")
            }
        }
    }
}"""
content = content.replace("\n}", load_method)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
