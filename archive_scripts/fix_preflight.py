import os
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_button = """                    Button(
                        onClick = { 
                            viewModel.startRecording("SGB Test Construction Site") 
                            cameraViewModel.startRecording()
                        },"""
new_button = """                    val context = LocalContext.current
                    Button(
                        onClick = {
                            // PRE-FLIGHT CHECK
                            if (cameraRecordingState == com.sgbdevapps.space360.service.CameraRecordingState.Disconnected || 
                                cameraRecordingState == com.sgbdevapps.space360.service.CameraRecordingState.Error) {
                                android.widget.Toast.makeText(context, "Cannot start: Insta360 is disconnected. Go to Settings.", android.widget.Toast.LENGTH_LONG).show()
                                return@Button
                            }
                            
                            viewModel.startRecording("SGB Test Construction Site") 
                            cameraViewModel.startRecording()
                        },"""

content = content.replace(old_button, new_button)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
