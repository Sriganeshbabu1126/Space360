import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add missing imports for Canvas/Offset
if "import androidx.compose.ui.geometry.Offset" not in content:
    content = content.replace("import androidx.compose.ui.graphics.Color", "import androidx.compose.ui.graphics.Color\nimport androidx.compose.ui.geometry.Offset\nimport androidx.compose.foundation.Canvas\nimport androidx.compose.ui.window.Dialog")

# Insert FloorPlanLocationPicker Composable at the end
dialog_composable = """
@Composable
fun FloorPlanLocationPicker(
    floorPlanUrl: String?,
    onLocationSelected: (latitude: Double, longitude: Double) -> Unit,
    onDismiss: () -> Unit
) {
    var selectedX by remember { mutableStateOf(0f) }
    var selectedY by remember { mutableStateOf(0f) }
    
    Dialog(onDismissRequest = onDismiss) {
        Card(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.fillMaxWidth().padding(16.dp)
            ) {
                Text(
                    "Tap floor plan to select start location",
                    style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Bold)
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                // Floor plan with click detection
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(300.dp)
                        .background(Color.LightGray)
                        .pointerInput(Unit) {
                            detectTapGestures { offset ->
                                selectedX = offset.x
                                selectedY = offset.y
                            }
                        }
                ) {
                    if (floorPlanUrl != null) {
                        AsyncImage(
                            model = floorPlanUrl,
                            contentDescription = "Floor plan for selection",
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Fit
                        )
                    }
                    
                    // Draw pin marker at selected location
                    if (selectedX > 0 && selectedY > 0) {
                        Canvas(modifier = Modifier.fillMaxSize()) {
                            drawCircle(
                                color = Color.Red,
                                radius = 20f,
                                center = Offset(selectedX, selectedY)
                            )
                            drawCircle(
                                color = Color.White,
                                radius = 8f,
                                center = Offset(selectedX, selectedY)
                            )
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Confirm/Cancel buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Button(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.surfaceVariant,
                            contentColor = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    ) {
                        Text("Cancel")
                    }
                    
                    Button(
                        onClick = {
                            val lat = selectedY.toDouble()
                            val lng = selectedX.toDouble()
                            onLocationSelected(lat, lng)
                        },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF1D9E75)
                        ),
                        enabled = selectedX > 0 && selectedY > 0
                    ) {
                        Text("Confirm")
                    }
                }
            }
        }
    }
}
"""
if "fun FloorPlanLocationPicker" not in content:
    content += dialog_composable

# Replace variables in CaptureScreen
old_vars = """    val pathRecordingState by cameraViewModel.pathRecordingState.collectAsState()
    val cameraRecordingState by cameraViewModel.cameraRecordingState.collectAsState()

    var pinOffset by remember { mutableStateOf(androidx.compose.ui.geometry.Offset.Zero) }"""

new_vars = """    val pathRecordingState by cameraViewModel.pathRecordingState.collectAsState()
    val cameraRecordingState by cameraViewModel.cameraRecordingState.collectAsState()
    
    val showLocationPicker by viewModel.showLocationPicker.collectAsState()
    val currentFloorPlanUrl by viewModel.currentFloorPlanUrl.collectAsState()
    val pinnedLocation by viewModel.pinnedLocation.collectAsState()

    var pinOffset by remember { mutableStateOf(androidx.compose.ui.geometry.Offset.Zero) }"""
content = content.replace(old_vars, new_vars)

# We need to replace `viewModel.pinLocation()` with `viewModel.openLocationPicker()`
# And add the Dialog call
old_button = """                // Step 1: Pin Location
                Button(
                    onClick = { viewModel.pinLocation() },"""
new_button = """                // Step 1: Pin Location
                Button(
                    onClick = { viewModel.openLocationPicker() },"""
content = content.replace(old_button, new_button)

# Also we need to show the FloorPlan on the main screen if there is one!
old_map = """            // Floor plan or map
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .background(Color.LightGray, RoundedCornerShape(8.dp)),
                contentAlignment = Alignment.Center
            ) {
                if (isLocationPinned) {
                    Icon(
                        Icons.Filled.LocationOn,
                        contentDescription = "Location pinned",
                        tint = Color.Red,
                        modifier = Modifier.size(48.dp)
                    )
                } else {
                    Text("Tap to pin your location", color = Color.Gray)
                }
            }"""

new_map = """            // Floor plan or map
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .background(Color.LightGray, RoundedCornerShape(8.dp)),
                contentAlignment = Alignment.Center
            ) {
                if (currentFloorPlanUrl != null) {
                    AsyncImage(
                        model = currentFloorPlanUrl,
                        contentDescription = "Floor plan",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                } else {
                    Text("No floor plan available", color = Color.Gray)
                }
                
                if (isLocationPinned) {
                    Icon(
                        Icons.Filled.LocationOn,
                        contentDescription = "Location pinned",
                        tint = Color.Red,
                        modifier = Modifier.size(48.dp)
                    )
                }
            }
            
            if (showLocationPicker) {
                FloorPlanLocationPicker(
                    floorPlanUrl = currentFloorPlanUrl,
                    onLocationSelected = { lat, lng -> viewModel.pinLocationInteractive(lat, lng) },
                    onDismiss = { viewModel.closeLocationPicker() }
                )
            }"""

content = content.replace(old_map, new_map)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a6 screen")
