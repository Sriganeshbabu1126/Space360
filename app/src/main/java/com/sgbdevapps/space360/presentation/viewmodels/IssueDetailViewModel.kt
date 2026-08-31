package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.data.network.NetworkConnectivityManager
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.domain.model.IssueComment
import com.sgbdevapps.space360.domain.model.IssuePhoto
import com.sgbdevapps.space360.domain.repository.AuthRepository
import com.sgbdevapps.space360.domain.repository.IssueRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class IssueDetailViewModel @Inject constructor(
    private val issueRepository: IssueRepository,
    private val authRepository: AuthRepository,
    private val networkConnectivity: NetworkConnectivityManager
) : ViewModel() {
    
    private val _issue = MutableStateFlow<Issue?>(null)
    val issue: StateFlow<Issue?> = _issue.asStateFlow()
    
    private val _comments = MutableStateFlow<List<IssueComment>>(emptyList())
    val comments: StateFlow<List<IssueComment>> = _comments.asStateFlow()
    
    private val _photos = MutableStateFlow<List<IssuePhoto>>(emptyList())
    val photos: StateFlow<List<IssuePhoto>> = _photos.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    private val _isOnline = MutableStateFlow(true)
    val isOnline: StateFlow<Boolean> = _isOnline.asStateFlow()
    
    private val _pendingSyncCount = MutableStateFlow(0)
    val pendingSyncCount: StateFlow<Int> = _pendingSyncCount.asStateFlow()
    
    private val _lastCacheUpdateTime = MutableStateFlow<Long?>(null)
    val lastCacheUpdateTime: StateFlow<Long?> = _lastCacheUpdateTime.asStateFlow()
    
    private val _isAdmin = MutableStateFlow(false)
    val isAdmin: StateFlow<Boolean> = _isAdmin.asStateFlow()
    
    init {
        viewModelScope.launch {
            networkConnectivity.isOnline.collect { online ->
                _isOnline.value = online
            }
        }
        
        viewModelScope.launch {
            issueRepository.observePendingSyncCount().collect { count ->
                _pendingSyncCount.value = count
            }
        }
        
        viewModelScope.launch {
            val user = authRepository.getCurrentUser().getOrNull()
            _isAdmin.value = user?.email == "wincadsg@gmail.com"
        }
    }
    
    fun loadIssueDetail(issueId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val result = issueRepository.getIssueById(issueId)
                val loadedIssue = result.getOrNull()
                _issue.value = loadedIssue
                _comments.value = loadedIssue?.comments ?: emptyList()
                _photos.value = loadedIssue?.photos ?: emptyList()
                _lastCacheUpdateTime.value = System.currentTimeMillis()
                
                if (result.isFailure) {
                    _error.value = result.exceptionOrNull()?.message
                }
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun updateIssueStatus(issueId: String, newStatus: String) {
        viewModelScope.launch {
            try {
                val userId = authRepository.getCurrentUser().getOrNull()?.id ?: ""
                val result = issueRepository.updateIssueStatus(
                    issueId = issueId,
                    newStatus = newStatus,
                    contractorId = userId
                )
                
                if (result.isSuccess) {
                    _issue.value = _issue.value?.copy(status = newStatus)
                    _error.value = null
                } else {
                    _error.value = result.exceptionOrNull()?.message
                }
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
    
    fun addComment(issueId: String, text: String) {
        viewModelScope.launch {
            try {
                val user = authRepository.getCurrentUser().getOrNull()
                val userId = user?.id ?: ""
                val userName = user?.displayName ?: "Current User"

                val result = issueRepository.addComment(
                    issueId = issueId,
                    text = text,
                    contractorId = userId
                )
                
                if (result.isSuccess) {
                    val newComment = IssueComment(
                        id = java.util.UUID.randomUUID().toString(),
                        issueId = issueId,
                        userId = userId,
                        userName = userName,
                        text = text,
                        createdAt = java.time.Instant.now().toString()
                    )
                    _comments.value = _comments.value + newComment
                    _error.value = null
                } else {
                    _error.value = result.exceptionOrNull()?.message
                }
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
    
    fun addPhotos(issueId: String, photoFilePaths: List<String>) {
        viewModelScope.launch {
            for (filePath in photoFilePaths) {
                try {
                    val result = issueRepository.addPhotoToIssue(
                        issueId = issueId,
                        filePath = filePath
                    )
                    
                    if (result.isSuccess) {
                        val newPhoto = IssuePhoto(
                            id = java.util.UUID.randomUUID().toString(),
                            issueId = issueId,
                            photoUrl = filePath,
                            uploadedAt = java.time.Instant.now().toString()
                        )
                        _photos.value = _photos.value + newPhoto
                    }
                } catch (e: Exception) {
                    _error.value = "Failed to upload photo: ${e.message}"
                }
            }
        }
    }
    
    fun clearError() {
        _error.value = null
    }
}
