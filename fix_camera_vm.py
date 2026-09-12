import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/CameraStateViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add a mock connected state for testing
mock = """    init {
        // For testing MVP Phase 4a without real camera, we mock it as connected
        viewModelScope.launch {
            // insta360SyncManager.mockConnect() // If it existed
            // We'll just rely on the pre-flight check in UI but let's not block testing.
        }
    }"""
    
# Actually, I will just update Insta360SyncManager to start as Connected for testing
