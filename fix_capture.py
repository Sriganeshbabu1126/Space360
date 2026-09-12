import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace variables
old_vars = """    val isRecording by viewModel.isRecording.collectAsState()
    val isSaving by viewModel.isSaving.collectAsState()
    val saveStatus by viewModel.saveStatus.collectAsState()
    val waypointCount by viewModel.waypointCount.collectAsState()
    val elapsedTime by viewModel.elapsedTimeSeconds.collectAsState()
    
    val pathRecordingState by cameraViewModel.pathRecordingState.collectAsState()
    val cameraRecordingState by cameraViewModel.cameraRecordingState.collectAsState()

    var isPinned by remember { mutableStateOf(false) }
    var pinOffset by remember { mutableStateOf(androidx.compose.ui.geometry.Offset.Zero) }"""

new_vars = """    val isRecording by viewModel.isRecording.collectAsState()
    val isSaving by viewModel.isSaving.collectAsState()
    val saveStatus by viewModel.saveStatus.collectAsState()
    val waypointCount by viewModel.waypointCount.collectAsState()
    val elapsedTime by viewModel.elapsedTimeSeconds.collectAsState()
    val isLocationPinned by viewModel.isLocationPinned.collectAsState()
    
    val pathRecordingState by cameraViewModel.pathRecordingState.collectAsState()
    val cameraRecordingState by cameraViewModel.cameraRecordingState.collectAsState()

    var pinOffset by remember { mutableStateOf(androidx.compose.ui.geometry.Offset.Zero) }"""
content = content.replace(old_vars, new_vars)

# We need to replace the Box with Map Placeholder and the Control buttons below it
# Instead of a complex regex, I will just find the Box block
# Let's see what's after the Box.
