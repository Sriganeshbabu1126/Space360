import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add import for UpdateIssueStatusRequest
if "import com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest" not in content:
    content = content.replace("import com.sgbdevapps.space360.data.remote.AddCommentRequest", "import com.sgbdevapps.space360.data.remote.AddCommentRequest\nimport com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest")

old_status = """    fun updateIssueStatus(newStatus: String) {
        val currentIssue = _issue.value ?: return
        // Update local state optimistically
        _issue.value = currentIssue.copy(status = newStatus)
        // Note: For full implementation we should call the API:
        // viewModelScope.launch { api.updateIssueStatus(...) }
    }"""
new_status = """    fun updateIssueStatus(newStatus: String) {
        val currentIssue = _issue.value ?: return
        // Update local state optimistically
        _issue.value = currentIssue.copy(status = newStatus)
        
        viewModelScope.launch {
            try {
                api.updateIssueStatus(currentIssue.id, UpdateIssueStatusRequest(newStatus))
            } catch (e: Exception) {
                Log.e(TAG, "Failed to update status on server", e)
                offlineSyncManager.queueAction("update_status", "issue", currentIssue.id, newStatus)
            }
        }
    }"""
if old_status in content:
    content = content.replace(old_status, new_status)

old_photo = """    fun uploadPhotoUri(uri: Uri) {
        val issueId = currentIssueId ?: return
        viewModelScope.launch {
            try {
                offlineSyncManager.queueAction("upload_photo", "issue", issueId, uri.toString())
            } catch (e: Exception) {
                Log.e(TAG, "Failed to queue photo upload", e)
            }
        }
    }"""
new_photo = """    fun uploadPhotoUri(uri: Uri) {
        val issueId = currentIssueId ?: return
        viewModelScope.launch {
            try {
                offlineSyncManager.queueAction("upload_photo", "issue", issueId, uri.toString())
                
                // Optimistic UI update
                val current = _issue.value ?: return@launch
                val newPhotos = current.photos.toMutableList()
                newPhotos.add(
                    com.sgbdevapps.space360.domain.model.IssuePhoto(
                        id = "temp_${System.currentTimeMillis()}",
                        issueId = issueId,
                        photoUrl = uri.toString(),
                        uploadedAt = "Just now"
                    )
                )
                _issue.value = current.copy(photos = newPhotos)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to queue photo upload", e)
            }
        }
    }"""
if old_photo in content:
    content = content.replace(old_photo, new_photo)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
