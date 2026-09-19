import os
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_button = """                            viewModel.startRecording("SGB Test Construction Site") 
                            cameraViewModel.startRecording()"""
new_button = """                            // 1. Send start command to camera
                            cameraViewModel.startRecording()
                            
                            // 2. We assume camera started successfully for MVP (in production we'd wait for callback)
                            // 3. Start GPS tracking
                            viewModel.startRecording("SGB Test Construction Site")"""

if old_button in content:
    content = content.replace(old_button, new_button)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
