import os
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import androidx.compose.ui.platform.LocalContext" not in content:
    content = content.replace("import androidx.compose.ui.unit.sp", "import androidx.compose.ui.unit.sp\nimport androidx.compose.ui.platform.LocalContext")

# Remove the inline val context = LocalContext.current and put it at the top
old_inline = """                    val context = LocalContext.current
                    Button("""
new_inline = """                    Button("""

if old_inline in content:
    content = content.replace(old_inline, new_inline)
    
    # insert at the top of CaptureScreen
    top_anchor = """    var pinOffset by remember { mutableStateOf(androidx.compose.ui.geometry.Offset.Zero) }"""
    new_top = """    var pinOffset by remember { mutableStateOf(androidx.compose.ui.geometry.Offset.Zero) }
    val context = LocalContext.current"""
    
    content = content.replace(top_anchor, new_top)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
