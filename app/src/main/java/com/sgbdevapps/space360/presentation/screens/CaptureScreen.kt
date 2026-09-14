package com.sgbdevapps.space360.presentation.screens

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Circle
import androidx.compose.material.icons.filled.Bluetooth
import androidx.compose.material.icons.filled.Videocam
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.animation.core.*
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.geometry.Offset
import androidx.compose.foundation.Canvas
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.platform.LocalContext
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.ui.input.pointer.pointerInput
import coil.compose.AsyncImage
import coil.request.ImageRequest
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.material.icons.outlined.Map
import com.sgbdevapps.space360.R
import androidx.compose.foundation.Image
import androidx.compose.ui.res.painterResource

import com.sgbdevapps.space360.presentation.viewmodels.PathCaptureViewModel
import com.sgbdevapps.space360.presentation.viewmodels.CameraStateViewModel
import com.sgbdevapps.space360.presentation.components.CameraControlButton
import com.sgbdevapps.space360.presentation.components.CameraConnectionStatus
import com.sgbdevapps.space360.service.SyncStatus
import com.sgbdevapps.space360.service.PathRecordingState
import com.sgbdevapps.space360.service.CameraRecordingState
import kotlinx.coroutines.launch

data class BluetoothStatus(
    val isConnected: Boolean,
    val batteryPercent: Int,
    val displayName: String
)

data class VideoStatus(
    val isRecording: Boolean,
    val displayName: String,
    val details: String
)

@Composable
fun CaptureScreen(
    navController: NavController,
    viewModel: PathCaptureViewModel = hiltViewModel(),
    cameraViewModel: CameraStateViewModel = hiltViewModel()
) {
    val isRecording by viewModel.isRecording.collectAsState()
    val isSaving by viewModel.isSaving.collectAsState()
    val saveStatus by viewModel.saveStatus.collectAsState()
    val waypointCount by viewModel.waypointCount.collectAsState()
    val elapsedTime by viewModel.elapsedTimeSeconds.collectAsState()
    val selectedSite by viewModel.selectedSite.collectAsState()
    val isLocationPinned by viewModel.isLocationPinned.collectAsState()
    
    val pathRecordingState by cameraViewModel.pathRecordingState.collectAsState()
    val cameraRecordingState by cameraViewModel.cameraRecordingState.collectAsState()
    val showLocationPicker by viewModel.showLocationPicker.collectAsState()
    
    val pinnedLocation by viewModel.pinnedLocation.collectAsState()

    var isPinned by remember { mutableStateOf(false) }
    var pinOffset by remember { mutableStateOf(androidx.compose.ui.geometry.Offset.Zero) }
    val context = LocalContext.current

    val permissionsToRequest = mutableListOf(
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION
    )
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS)
    }
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        permissionsToRequest.add(Manifest.permission.BLUETOOTH_SCAN)
        permissionsToRequest.add(Manifest.permission.BLUETOOTH_CONNECT)
    } else {
        permissionsToRequest.add(Manifest.permission.BLUETOOTH)
        permissionsToRequest.add(Manifest.permission.BLUETOOTH_ADMIN)
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(permissionsToRequest.toTypedArray())
    }

    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        if (isSaving || saveStatus != null) {
            Box(
                modifier = Modifier.fillMaxWidth().weight(1f),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    if (isSaving) {
                        CircularProgressIndicator()
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                    Text(saveStatus ?: "Saving Path...", style = MaterialTheme.typography.titleLarge)
                }
            }
        } else {
            // Map Placeholder
            Box(modifier = Modifier.fillMaxWidth().height(300.dp)) {
                FloorPlanSection(viewModel)
                if (isLocationPinned) {
                    Icon(
                        Icons.Filled.LocationOn,
                        contentDescription = "Location pinned",
                        tint = Color.Red,
                        modifier = Modifier.size(48.dp).align(Alignment.Center)
                    )
                }
            }
            
            if (showLocationPicker) {
                val floorPlanUrl = (viewModel.floorPlanLoadState.collectAsState().value as? FloorPlanLoadState.Loaded)?.url
                FloorPlanLocationPicker(
                    floorPlanUrl = floorPlanUrl,
                    onLocationSelected = { lat, lng -> viewModel.pinLocationInteractive(lat, lng) },
                    onDismiss = { viewModel.closeLocationPicker() }
                )
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Recording Status Card
            RecordingStatusCard(
                isRecording = isRecording,
                recordingDurationSeconds = elapsedTime,
                waypointCount = waypointCount,
                gpsAccuracy = 5f,
                bluetoothStatus = BluetoothStatus(
                    isConnected = true,
                    batteryPercent = 95,
                    displayName = "Connected"
                ),
                videoStatus = VideoStatus(
                    isRecording = cameraRecordingState == CameraRecordingState.Recording,
                    displayName = if (cameraRecordingState == CameraRecordingState.Recording) "Recording" else "Ready",
                    details = "Awaiting Sync"
                )
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Pin/Start Button
            if (!isLocationPinned) {
                // Step 1: Pin Location
                Button(
                    onClick = { viewModel.openLocationPicker() },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp)
                        .padding(horizontal = 16.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF2196F3)
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.Filled.LocationOn, contentDescription = "Pin")
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        "📍 Pin Your Start Location",
                        style = MaterialTheme.typography.bodyLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    )
                }
            } else {
                // Step 2: Start Recording (after pinned)
                if (!isRecording) {
                    Button(
                        onClick = {
                            // PRE-FLIGHT CHECK
                            if (cameraRecordingState == com.sgbdevapps.space360.service.CameraRecordingState.Disconnected || 
                                cameraRecordingState == com.sgbdevapps.space360.service.CameraRecordingState.Error) {
                                android.widget.Toast.makeText(context, "Cannot start: Insta360 is disconnected. Go to Settings.", android.widget.Toast.LENGTH_LONG).show()
                                return@Button
                            }
                            
                            // 1. Send start command to camera
                            cameraViewModel.startRecording()
                            
                            // 2. We assume camera started successfully for MVP (in production we'd wait for callback)
                            // 3. Start GPS tracking
                            viewModel.startRecording(selectedSite?.name ?: "Unknown Site")
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp)
                            .padding(horizontal = 16.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF1D9E75)
                        ),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Filled.PlayArrow, contentDescription = "Start")
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            "🎬 Start Recording",
                            style = MaterialTheme.typography.bodyLarge.copy(
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        )
                    }
                } else {
                    // Step 3: Stop/Pause (while recording)
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Button(
                            onClick = { 
                                viewModel.pauseRecording() 
                                cameraViewModel.stopRecording()
                            },
                            modifier = Modifier
                                .weight(1f)
                                .height(56.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFFFC107)
                            )
                        ) {
                            Text("⏸️ Pause", color = Color.Black)
                        }
                        
                        Button(
                            onClick = { 
                                viewModel.stopRecording() 
                                cameraViewModel.stopRecording()
                                viewModel.unpinLocation()
                            },
                            modifier = Modifier
                                .weight(1f)
                                .height(56.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFD32F2F)
                            )
                        ) {
                            Text("⏹️ Stop", color = Color.White)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun RecordingStatusCard(
    isRecording: Boolean,
    recordingDurationSeconds: Int,
    waypointCount: Int,
    gpsAccuracy: Float,
    bluetoothStatus: BluetoothStatus,
    videoStatus: VideoStatus
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            
            // Insta Recording Status
            if (isRecording) {
                val infiniteTransition = rememberInfiniteTransition(label = "recording_blink")
                val alpha by infiniteTransition.animateFloat(
                    initialValue = 1f,
                    targetValue = 0.2f,
                    animationSpec = infiniteRepeatable(
                        animation = tween(800, easing = LinearEasing),
                        repeatMode = RepeatMode.Reverse
                    ),
                    label = "alpha_blink"
                )

                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        "🎥 Insta360 Recording Status: ACTIVE",
                        style = MaterialTheme.typography.titleMedium.copy(
                            color = Color.Gray,
                            fontWeight = FontWeight.SemiBold
                        )
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Filled.Circle,
                            contentDescription = "Recording",
                            tint = Color.Red,
                            modifier = Modifier
                                .size(16.dp)
                                .clip(CircleShape)
                                .alpha(alpha)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = formatDuration(recordingDurationSeconds),
                            style = MaterialTheme.typography.headlineSmall.copy(
                                fontSize = 36.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color.Black
                            )
                        )
                    }
                }
                Spacer(modifier = Modifier.height(20.dp))
            }
            
            // GPS Status
            StatusRow(
                icon = Icons.Filled.LocationOn,
                label = "GPS",
                status = if (isRecording) "Recording" else "Ready",
                details = "Accuracy: ±${gpsAccuracy.toInt()}m | Waypoints: $waypointCount",
                color = Color(0xFF4CAF50)  // Green
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            HorizontalDivider(modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(12.dp))
            
            // Bluetooth Status
            StatusRow(
                icon = Icons.Filled.Bluetooth,
                label = "Camera",
                status = bluetoothStatus.displayName,
                details = "Insta360 X4 • Battery ${bluetoothStatus.batteryPercent}%",
                color = if (bluetoothStatus.isConnected) Color(0xFF2196F3) else Color.Gray
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            HorizontalDivider(modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(12.dp))
            
            // Video Recording Status
            StatusRow(
                icon = Icons.Filled.Videocam,
                label = "Video",
                status = videoStatus.displayName,
                details = videoStatus.details,
                color = Color(0xFFFF9800)  // Orange
            )
        }
    }
}

@Composable
fun StatusRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    status: String,
    details: String,
    color: Color
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = color,
            modifier = Modifier.size(24.dp)
        )
        
        Spacer(modifier = Modifier.width(12.dp))
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "$label: $status",
                style = MaterialTheme.typography.bodyMedium.copy(
                    fontWeight = FontWeight.Bold,
                    color = Color.Black
                )
            )
            Text(
                text = details,
                style = MaterialTheme.typography.bodySmall.copy(
                    color = Color.Gray,
                    fontSize = 12.sp
                )
            )
        }
    }
}

fun formatDuration(seconds: Int): String {
    val mins = seconds / 60
    val secs = seconds % 60
    return String.format("%02d:%02d", mins, secs)
}

@Composable
fun RecordingControlButtons(
    isRecording: Boolean,
    isPaused: Boolean,
    onStartRecording: () -> Unit,
    onStopRecording: () -> Unit,
    onPauseRecording: () -> Unit,
    onResumeRecording: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        if (!isRecording) {
            // Start Button (Large, prominent)
            Button(
                onClick = onStartRecording,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF1D9E75)  // Brand teal
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(
                    Icons.Filled.PlayArrow,
                    contentDescription = "Start",
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    "🎬 Start Recording",
                    style = MaterialTheme.typography.bodyLarge.copy(
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                )
            }
        } else {
            // Recording Controls
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Pause Button
                Button(
                    onClick = if (isPaused) onResumeRecording else onPauseRecording,
                    modifier = Modifier
                        .weight(1f)
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFFFFC107)  // Amber
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(
                        if (isPaused) Icons.Filled.PlayArrow else Icons.Filled.Pause,
                        contentDescription = "Pause/Resume",
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(if (isPaused) "Resume" else "Pause")
                }
                
                // Stop Button
                Button(
                    onClick = onStopRecording,
                    modifier = Modifier
                        .weight(1f)
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFFD32F2F)  // Red
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(
                        Icons.Filled.Stop,
                        contentDescription = "Stop",
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Stop")
                }
            }
        }
    }
}

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


@Composable
fun FloorPlanSection(viewModel: com.sgbdevapps.space360.presentation.viewmodels.PathCaptureViewModel) {
    val state by viewModel.floorPlanLoadState.collectAsState()

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(280.dp)
            .padding(horizontal = 16.dp, vertical = 8.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            when (state) {
                // Loading spinner
                is FloorPlanLoadState.Loading -> {
                    Box(
                        modifier = Modifier.fillMaxSize()
                            .background(MaterialTheme.colorScheme.surfaceVariant),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text("Loading floor plan...",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                }
                // LAYER 1: Real floor plan from backend
                is FloorPlanLoadState.Loaded -> {
                    val url = (state as FloorPlanLoadState.Loaded).url
                    AsyncImage(
                        model = ImageRequest.Builder(LocalContext.current)
                            .data(url)
                            .crossfade(true)
                            .placeholder(R.drawable.floor_plan_placeholder)
                            .error(R.drawable.floor_plan_placeholder)
                            .build(),
                        contentDescription = "Floor plan",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                    Box(modifier = Modifier.fillMaxSize().padding(8.dp),
                        contentAlignment = Alignment.TopStart) {
                        Surface(color = MaterialTheme.colorScheme.primary.copy(alpha = 0.75f),
                            shape = RoundedCornerShape(4.dp)) {
                            Text("Floor Plan",
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.White)
                        }
                    }
                }
                // LAYER 2: No floor plan uploaded
                is FloorPlanLoadState.NoFloorPlan -> {
                    Box(modifier = Modifier.fillMaxSize()) {
                        Image(
                            painter = painterResource(id = R.drawable.floor_plan_placeholder),
                            contentDescription = "Floor plan placeholder",
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Fit
                        )
                        Box(modifier = Modifier.fillMaxSize().padding(8.dp),
                            contentAlignment = Alignment.BottomCenter) {
                            Surface(color = Color.Black.copy(alpha = 0.45f),
                                shape = RoundedCornerShape(4.dp)) {
                                Text("No floor plan uploaded for this project",
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                    style = MaterialTheme.typography.labelSmall,
                                    color = Color.White)
                            }
                        }
                    }
                }
                // LAYER 3: No project selected or error
                is FloorPlanLoadState.NoProject,
                is FloorPlanLoadState.Error -> {
                    Box(
                        modifier = Modifier.fillMaxSize()
                            .background(MaterialTheme.colorScheme.surfaceVariant),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally,
                            modifier = Modifier.padding(16.dp)) {
                            Icon(imageVector = Icons.Outlined.Map,
                                contentDescription = null,
                                modifier = Modifier.size(48.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                if (state is FloorPlanLoadState.NoProject)
                                    "Select a project to view floor plan"
                                else
                                    "Floor plan unavailable",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                }
            }
        }
    }
}
