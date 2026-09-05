package com.sgbdevapps.space360.presentation.screens

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.ui.input.pointer.pointerInput
import coil.compose.AsyncImage
import com.sgbdevapps.space360.presentation.viewmodels.PathCaptureViewModel
import kotlinx.coroutines.launch

@Composable
fun CaptureScreen(
    navController: NavController,
    viewModel: PathCaptureViewModel = hiltViewModel()
) {
    val isRecording by viewModel.isRecording.collectAsState()
    val isSaving by viewModel.isSaving.collectAsState()
    val waypointCount by viewModel.waypointCount.collectAsState()
    val elapsedTime by viewModel.elapsedTimeSeconds.collectAsState()

    var isPinned by remember { mutableStateOf(false) }
    var pinOffset by remember { mutableStateOf(androidx.compose.ui.geometry.Offset.Zero) }

    val permissionsToRequest = mutableListOf(
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION
    )
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS)
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        // Handle permissions
    }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(permissionsToRequest.toTypedArray())
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Path Capture (GPS Tracking)",
            style = MaterialTheme.typography.headlineMedium
        )
        Spacer(modifier = Modifier.height(16.dp))

        if (isSaving) {
            Box(
                modifier = Modifier.fillMaxWidth().weight(1f),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Saving Path...", style = MaterialTheme.typography.titleLarge)
                }
            }
        } else if (isRecording) {
            Card(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("Recording Active", style = MaterialTheme.typography.titleLarge)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Waypoints: $waypointCount", style = MaterialTheme.typography.bodyLarge)
                    val mins = elapsedTime / 60
                    val secs = elapsedTime % 60
                    val secsStr = secs.toString().padStart(2, '0')
                    Text("Time: ${mins}:${secsStr}", style = MaterialTheme.typography.bodyLarge)

                    Spacer(modifier = Modifier.height(16.dp))
                    Row {
                        Button(
                            onClick = {
                                viewModel.stopRecording()
                                isPinned = false
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
                        ) {
                            Text("Stop Recording")
                        }
                        Spacer(modifier = Modifier.width(16.dp))
                        OutlinedButton(
                            onClick = {
                                viewModel.discardRecording()
                                isPinned = false
                            }
                        ) {
                            Text("Cancel")
                        }
                    }
                }
            }
        } else {
            // Map Placeholder
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .background(Color.LightGray)
                    .clickable { 
                        // Simulate tap
                    },
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
                } else {
                    Text("Tap on floor plan to pin start location", color = Color.DarkGray)
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = {
                    viewModel.startRecording("SGB Test Construction Site")
                },
                enabled = isPinned,
                modifier = Modifier.fillMaxWidth().height(56.dp)
            ) {
                Text("Start Recording")
            }
        }
    }
}
