package com.sgbdevapps.space360.presentation.viewmodels

import android.graphics.Bitmap
import android.net.Uri
import android.util.Log
import timber.log.Timber
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.data.remote.IssuesService
import com.sgbdevapps.space360.data.remote.AddCommentRequest
import com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.service.OfflineSyncManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import javax.inject.Inject

import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext

@HiltViewModel
class IssueDetailViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val api: IssuesService,
    private val issueRepository: com.sgbdevapps.space360.domain.repository.IssueRepository,
    private val offlineSyncManager: OfflineSyncManager
) : ViewModel() {
    
    private val TAG = "IssueDetailViewModel"
    
    private val _issue = MutableStateFlow<Issue?>(null)
    val issue = _issue.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error = _error.asStateFlow()
    

    private val _isUploadingPhoto = MutableStateFlow(false)
    val isUploadingPhoto = _isUploadingPhoto.asStateFlow()
    
    private val _photoUploadError = MutableStateFlow<String?>(null)
    val photoUploadError = _photoUploadError.asStateFlow()
    
    private var currentIssueId: String? = null
    

    fun updateIssueStatus(newStatus: String) {
        val currentIssue = _issue.value ?: return
        // Update local state optimistically
        _issue.value = currentIssue.copy(status = newStatus)
        
        viewModelScope.launch {
            try {
                Timber.d("STATUS_DEBUG: updating issue ${currentIssue.id} to $newStatus")
                api.updateIssueStatus(currentIssue.id, UpdateIssueStatusRequest(newStatus))
                // Re-fetch to confirm
                loadIssue(currentIssue.id)
                Timber.i("STATUS_DEBUG: status updated successfully")
            } catch (e: Exception) {
                Timber.e(e, "STATUS_DEBUG: update failed")
                offlineSyncManager.queueAction("update_status", "issue", currentIssue.id, UpdateIssueStatusRequest(newStatus))
            }
        }
    }

    fun loadIssue(issueId: String) {
        currentIssueId = issueId
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                val fetched = api.getIssueById(issueId)
                
                val domainComments = fetched.comments?.map { 
                    com.sgbdevapps.space360.domain.model.IssueComment(
                        id = it.id,
                        issueId = issueId,
                        userId = "unknown",
                        userName = it.user_name,
                        text = it.text,
                        createdAt = it.created_at
                    )
                } ?: emptyList()
                
                val domainPhotos = fetched.photos?.map {
                    com.sgbdevapps.space360.domain.model.IssuePhoto(
                        id = it.id,
                        issueId = issueId,
                        photoUrl = it.photo_url,
                        uploadedAt = it.uploaded_at ?: ""
                    )
                } ?: emptyList()
                
                _issue.value = Issue(
                    id = fetched.id, 
                    title = fetched.title, 
                    description = fetched.description ?: "", 
                    status = fetched.status, 
                    priority = fetched.priority ?: "", 
                    siteId = fetched.site_id, 
                    assignedTo = "", 
                    assignedToName = "", 
                    createdAt = "", 
                    updatedAt = "", 
                    comments = domainComments,
                    photos = domainPhotos
                )
            } catch (e: Exception) {
                Log.e(TAG, "Failed to load issue", e)
                _error.value = "Could not load issue"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun uploadPhotoBitmap(bitmap: Bitmap) {
        val issueId = currentIssueId ?: return
        // Pseudo code for MVP, converting Bitmap to multipart is complex for python generation
        // Ideally we save to file, get URI, then upload.
        // Queueing offline photo upload
        viewModelScope.launch {
            try {
                offlineSyncManager.queueAction("upload_photo", "issue", issueId, "file_path_placeholder")
            } catch (e: Exception) {
                Log.e(TAG, "Failed to queue photo upload", e)
            }
        }
    }
    
    fun addPhotoToIssue(issueId: String, photoUri: Uri) {
        viewModelScope.launch {
            try {
                _isUploadingPhoto.value = true
                Timber.d("PHOTO_DEBUG: starting upload issueId=$issueId uri=$photoUri")

                val contentResolver = context.contentResolver
                val inputStream = contentResolver.openInputStream(photoUri)
                    ?: throw Exception("Cannot open image stream")

                val bytes = inputStream.readBytes()
                inputStream.close()

                val requestBody = okhttp3.RequestBody.create("image/jpeg".toMediaTypeOrNull(), bytes)
                val multipart = okhttp3.MultipartBody.Part.createFormData(
                    "photo", "photo_${System.currentTimeMillis()}.jpg", requestBody
                )

                api.uploadPhoto(issueId, multipart)

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
    }
    
    fun addComment(text: String) {
        val issueId = currentIssueId ?: return
        viewModelScope.launch {
            try {
                api.addComment(issueId, AddCommentRequest(text))
                // Reload immediately
                loadIssue(issueId)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to add comment", e)
                offlineSyncManager.queueAction("add_comment", "issue", issueId, AddCommentRequest(text))
                
                // Optimistic UI update
                val current = _issue.value ?: return@launch
                val newComments = current.comments.toMutableList()
                newComments.add(
                    com.sgbdevapps.space360.domain.model.IssueComment(
                        id = "temp_${System.currentTimeMillis()}",
                        issueId = issueId,
                        userId = "current_user",
                        userName = "You (Offline)",
                        text = text,
                        createdAt = "Just now"
                    )
                )
                _issue.value = current.copy(comments = newComments)
            }
        }
    }
}
