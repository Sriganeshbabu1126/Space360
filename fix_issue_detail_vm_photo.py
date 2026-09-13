import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add missing state flows
if "private val _isUploadingPhoto" not in content:
    old_state = """    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()"""
    new_state = """    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    private val _isUploadingPhoto = MutableStateFlow(false)
    val isUploadingPhoto: StateFlow<Boolean> = _isUploadingPhoto.asStateFlow()

    private val _photoUploadError = MutableStateFlow<String?>(null)
    val photoUploadError: StateFlow<String?> = _photoUploadError.asStateFlow()"""
    content = content.replace(old_state, new_state)

# Replace uploadPhotoUri with addPhotoToIssue
old_upload = """    fun uploadPhotoUri(uri: Uri) {
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
new_upload = """    fun addPhotoToIssue(issueId: String, photoUri: Uri) {
        viewModelScope.launch {
            try {
                _isUploadingPhoto.value = true
                Timber.d("PHOTO_DEBUG: starting upload issueId=$issueId uri=$photoUri")

                val contentResolver = getApplication<android.app.Application>().contentResolver
                val inputStream = contentResolver.openInputStream(photoUri)
                    ?: throw Exception("Cannot open image stream")

                val bytes = inputStream.readBytes()
                inputStream.close()

                val requestBody = okhttp3.RequestBody.create(okhttp3.MediaType.parse("image/jpeg"), bytes)
                val multipart = okhttp3.MultipartBody.Part.createFormData(
                    "photo", "photo_${System.currentTimeMillis()}.jpg", requestBody
                )

                // POST /api/issues/{issueId}/photos
                val apiService = com.sgbdevapps.space360.di.NetworkModule.provideRetrofit(
                    com.sgbdevapps.space360.di.NetworkModule.provideGson(),
                    com.sgbdevapps.space360.di.NetworkModule.provideOkHttpClient(
                        com.sgbdevapps.space360.di.NetworkModule.provideAuthInterceptor(getApplication<android.app.Application>()),
                        com.sgbdevapps.space360.di.NetworkModule.provideLoggingInterceptor()
                    )
                ).create(com.sgbdevapps.space360.data.remote.IssuesService::class.java)

                apiService.uploadIssuePhoto(issueId, multipart)

                Timber.d("PHOTO_DEBUG: upload successful — refreshing issue")

                val result = issueRepository.getIssueById(issueId)
                if (result.isSuccess) {
                    _issue.value = result.getOrNull()
                }

                Timber.i("Photo uploaded + issue refreshed for $issueId")

            } catch (e: Exception) {
                Timber.e(e, "PHOTO_DEBUG: upload FAILED — ${e.message}")
                _photoUploadError.value = e.message ?: "Photo upload failed"
            } finally {
                _isUploadingPhoto.value = false
            }
        }
    }"""
if old_upload in content:
    content = content.replace(old_upload, new_upload)
else:
    print("Failed to replace uploadPhotoUri")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
