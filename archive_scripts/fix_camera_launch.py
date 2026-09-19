import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_launch = """            photoUri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                tempFile
            )
            cameraLauncher.launch(photoUri!!)"""
new_launch = """            photoUri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                tempFile
            )
            try {
                cameraLauncher.launch(photoUri!!)
            } catch (e: Exception) {
                android.widget.Toast.makeText(context, "No camera app found", android.widget.Toast.LENGTH_SHORT).show()
            }"""
if old_launch in content:
    content = content.replace(old_launch, new_launch)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
