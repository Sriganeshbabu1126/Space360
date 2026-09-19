import os
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('Text("⏹️ Stop")', 'Text("⏹️ Stop", color = Color.White)')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a8 screen 2")
