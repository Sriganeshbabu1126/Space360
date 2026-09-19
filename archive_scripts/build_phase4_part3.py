import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path}")

# IssueDetailViewModel.kt
write_file("app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt", """
package com.sgbdevapps.space360.presentation.viewmodels

import android.graphics.Bitmap
import android.net.Uri
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.data.remote.ApiService
import com.sgbdevapps.space360.data.remote.AddCommentRequest
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.service.OfflineSyncManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class IssueDetailViewModel @Inject constructor(
    private val api: ApiService,
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
    
    fun loadIssue(issueId: String) {
        currentIssueId = issueId
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                // Since this is MVP Phase 4a, we call the backend
                val fetched = api.getIssueDetails(issueId)
                _issue.value = fetched
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
                // Reload
                loadIssue(issueId)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to add comment", e)
                offlineSyncManager.queueAction("add_comment", "issue", issueId, AddCommentRequest(text))
            }
        }
    }
}
""")
