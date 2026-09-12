import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# I will replace from `            // Map Placeholder` up to the end of the CaptureScreen function

old_section = content.split("            // Map Placeholder")[1].split("        }\n    }\n}")[0]

new_section = """
            // Floor plan or map
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
                    onClick = { viewModel.pinLocation() },
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
                            viewModel.startRecording("SGB Test Construction Site") 
                            cameraViewModel.startRecording()
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
                            onClick = { },
                            modifier = Modifier
                                .weight(1f)
                                .height(56.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFFFC107)
                            )
                        ) {
                            Text("⏸️ Pause")
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
                            Text("⏹️ Stop")
                        }
                    }
                }
            }
"""
content = content.replace(old_section, new_section)
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
