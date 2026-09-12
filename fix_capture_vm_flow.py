import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/PathCaptureViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add kotlinx.coroutines.flow operators
if "import kotlinx.coroutines.flow.filterNotNull" not in content:
    content = content.replace("import kotlinx.coroutines.flow.collectLatest", "import kotlinx.coroutines.flow.collectLatest\nimport kotlinx.coroutines.flow.filterNotNull\nimport kotlinx.coroutines.flow.distinctUntilChanged\nimport timber.log.Timber")

old_init = """    init {
        loadFloorPlan()"""
new_init = """    init {
        // Observe active project as a Flow
        viewModelScope.launch {
            sessionManager.selectedSite
                .filterNotNull()
                .distinctUntilChanged()
                .collect { site ->
                    loadFloorPlan(site.id)
                }
        }
        
        // Safety timeout
        viewModelScope.launch {
            kotlinx.coroutines.delay(6_000)
            if (_floorPlanLoadState.value is com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loading) {
                Timber.w("Floor plan load timed out - showing placeholder")
                _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.NoFloorPlan
            }
        }"""
if old_init in content:
    content = content.replace(old_init, new_init)

old_load = """    private fun loadFloorPlan() {
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
    }"""
new_load = """    private suspend fun loadFloorPlan(projectId: String) {
        try {
            _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loading
            
            // Re-fetch site just in case, but we already have it from sessionManager
            val site = sessionManager.selectedSite.value
            val url = site?.floorPlanUrl
            
            _floorPlanLoadState.value = if (!url.isNullOrBlank()) {
                com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loaded(url)
            } else {
                com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.NoFloorPlan
            }
        } catch (e: Exception) {
            Timber.e(e, "loadFloorPlan failed")
            _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.NoFloorPlan
        }
    }"""
if old_load in content:
    content = content.replace(old_load, new_load)
else:
    print("Could not find old_load")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
