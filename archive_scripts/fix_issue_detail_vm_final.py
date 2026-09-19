import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add missing state properties
new_props = """
    private val _isUploadingPhoto = MutableStateFlow(false)
    val isUploadingPhoto = _isUploadingPhoto.asStateFlow()
    
    private val _photoUploadError = MutableStateFlow<String?>(null)
    val photoUploadError = _photoUploadError.asStateFlow()
    
    private var currentIssueId: String? = null"""
content = content.replace("    private var currentIssueId: String? = null", new_props)

# Fix okhttp3.MediaType.parse deprecation warning
content = content.replace('okhttp3.MediaType.parse("image/jpeg")', 'okhttp3.MediaType.Companion.toMediaTypeOrNull("image/jpeg")!!')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
