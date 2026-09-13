import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add import if missing
if "import okhttp3.MediaType.Companion.toMediaTypeOrNull" not in content:
    content = content.replace("import timber.log.Timber", "import timber.log.Timber\nimport okhttp3.MediaType.Companion.toMediaTypeOrNull")

content = content.replace(
    'okhttp3.MediaType.parse("image/jpeg")', 
    '"image/jpeg".toMediaTypeOrNull()'
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
