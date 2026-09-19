import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add scroll import
if "import androidx.compose.foundation.verticalScroll" not in content:
    content = content.replace("import androidx.compose.foundation.layout.*", "import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.verticalScroll\nimport androidx.compose.foundation.rememberScrollState")

old_col = """    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {"""
new_col = """    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {"""

if old_col in content:
    content = content.replace(old_col, new_col)

# Fix emojis
content = content.replace("?? Pin Your Start Location", "📍 Pin Your Start Location")
content = content.replace("?? Start Recording", "🎬 Start Recording")
content = content.replace("?? Pause", "⏸ Pause")
content = content.replace("?? Stop", "⏹ Stop")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
