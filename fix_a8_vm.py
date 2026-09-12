import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/PathCaptureViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add pauseRecording
new_pause = """
    fun pauseRecording() {
        _isRecording.value = false
        timerJob?.cancel()
        waypointJob?.cancel()
        // Stop the GPS tracking service intent in a real scenario
    }
"""

if "fun pauseRecording" not in content:
    content = content.replace("fun stopRecording()", new_pause + "\n    fun stopRecording()")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a8 vm")
