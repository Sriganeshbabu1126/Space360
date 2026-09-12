package com.sgbdevapps.space360.presentation.viewmodels

import android.graphics.Bitmap
import android.net.Uri
import android.util.Log
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

@HiltViewModel
class IssueDetailViewModel @Inject constructor(
    private val api: IssuesService,
    private val offlineSyncManager: OfflineSyncManager
) : ViewModel() {
    
    private val TAG = "IssueDetailViewModel"
    
    private val _issue = MutableStateFlow<Issue?>(null)
    val issue = _issue.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error = _error.asStateFlow()
    
    private var currentIssueId: String? = null
    

    fun updateIssueStatus(newStatus: String) {
        val currentIssue = _issue.value ?: return
        // Update local state optimistically
        _issue.value = currentIssue.copy(status = newStatus)
        
        viewModelScope.launch {
            try {
                api.updateIssueStatus(currentIssue.id, UpdateIssueStatusRequest(newStatus))
            } catch (e: Exception) {
                Log.e(TAG, "Failed to update status on server", e)
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
    
    fun uploadPhotoUri(uri: Uri) {
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
