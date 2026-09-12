import os
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("?? Pin Your Start Location", "📍 Pin Your Start Location")
content = content.replace("?? Start Recording", "🎬 Start Recording")
content = content.replace("?? Pause", "⏸ Pause")
content = content.replace("?? Stop", "⏹ Stop")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
