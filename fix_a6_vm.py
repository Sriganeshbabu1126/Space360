import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/PathCaptureViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_props = """
    private val _showLocationPicker = MutableStateFlow(false)
    val showLocationPicker: StateFlow<Boolean> = _showLocationPicker
    
    private val _pinnedLocation = MutableStateFlow<Pair<Double, Double>?>(null)
    val pinnedLocation: StateFlow<Pair<Double, Double>?> = _pinnedLocation
    
    val currentFloorPlanUrl = MutableStateFlow<String?>("file:///android_asset/L1.jpg") // Mock URL for MVP
    
    fun openLocationPicker() {
        _showLocationPicker.value = true
    }
    
    fun closeLocationPicker() {
        _showLocationPicker.value = false
    }
    
    fun pinLocationInteractive(lat: Double, lng: Double) {
        _pinnedLocation.value = Pair(lat, lng)
        _isLocationPinned.value = true
        _showLocationPicker.value = false
    }
"""

# Insert new properties in PathCaptureViewModel
if "fun openLocationPicker()" not in content:
    # Just replace fun pinLocation with the new interactive one
    old_pin_loc = """    fun pinLocation() {
        _isLocationPinned.value = true
        // CrashlyticsHelper.logEvent("Location pinned for recording")
    }"""
    
    content = content.replace(old_pin_loc, old_pin_loc + new_props)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a6 vm")
