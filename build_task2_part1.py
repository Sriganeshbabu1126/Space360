import os

CAPTURE_SCREEN_PATH = r"F:\Space360\app\src\main\java\com\sgbdevapps\space360\presentation\screens\CaptureScreen.kt"

CAPTURE_CONTENT = """package com.sgbdevapps.space360.presentation.screens

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
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
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.ui.input.pointer.pointerInput
import coil.compose.AsyncImage
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
    
    val pathRecordingState by cameraViewModel.pathRecordingState.collectAsState()
    val cameraRecordingState by cameraViewModel.cameraRecordingState.collectAsState()

    var isPinned by remember { mutableStateOf(false) }
    var pinOffset by remember { mutableStateOf(androidx.compose.ui.geometry.Offset.Zero) }

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
        modifier = Modifier.fillMaxSize(),
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
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .background(Color.LightGray)
                    .clickable { },
                contentAlignment = Alignment.Center
            ) {
                AsyncImage(
                    model = "file:///android_asset/L1.jpg",
                    contentDescription = "Floor Plan L1",
                    modifier = Modifier
                        .fillMaxSize()
                        .pointerInput(Unit) {
                            detectTapGestures(
                                onTap = { offset ->
                                    isPinned = true
                                    pinOffset = offset
                                }
                            )
                        },
                    contentScale = ContentScale.Fit
                )
                
                if (isPinned) {
                    Icon(
                        imageVector = Icons.Default.LocationOn,
                        contentDescription = "Pin",
                        tint = Color.Red,
                        modifier = Modifier
                            .offset { IntOffset(pinOffset.x.toInt() - 36, pinOffset.y.toInt() - 72) }
                            .size(36.dp)
                    )
                }
            }

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

            RecordingControlButtons(
                isRecording = isRecording,
                isPaused = false,
                onStartRecording = {
                    if (isPinned) {
                        viewModel.startRecording()
                        cameraViewModel.startRecording()
                    }
                },
                onStopRecording = {
                    viewModel.stopRecording()
                    cameraViewModel.stopRecording()
                    isPinned = false
                },
                onPauseRecording = { },
                onResumeRecording = { }
            )
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
            
            // Recording Timer (Large, Bold)
            if (isRecording) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Filled.Circle,
                        contentDescription = "Recording",
                        tint = Color.Red,
                        modifier = Modifier
                            .size(12.dp)
                            .clip(CircleShape)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = formatDuration(recordingDurationSeconds),
                        style = MaterialTheme.typography.headlineSmall.copy(
                            fontSize = 36.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.Black
                        )
                    )
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
"""

with open(CAPTURE_SCREEN_PATH, "w", encoding="utf-8") as f:
    f.write(CAPTURE_CONTENT)
print("Updated CaptureScreen.kt")
