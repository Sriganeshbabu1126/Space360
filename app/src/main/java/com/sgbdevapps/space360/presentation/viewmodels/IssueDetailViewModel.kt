package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.domain.repository.IssueRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class IssueDetailViewModel @Inject constructor(
    private val issueRepository: IssueRepository
) : ViewModel() {

    private val _issue = MutableStateFlow<Issue?>(null)
    val issue: StateFlow<Issue?> = _issue

    private val _issueDetailState = MutableStateFlow<IssueDetailState>(IssueDetailState.Idle)
    val issueDetailState: StateFlow<IssueDetailState> = _issueDetailState

    private val _updateState = MutableStateFlow<UpdateState>(UpdateState.Idle)
    val updateState: StateFlow<UpdateState> = _updateState

    fun loadIssue(issueId: Int) {
        viewModelScope.launch {
            _issueDetailState.value = IssueDetailState.Loading
            val result = issueRepository.getIssueById(issueId)
            if (result.isSuccess) {
                _issue.value = result.getOrNull()
                _issueDetailState.value = IssueDetailState.Success
            } else {
                _issueDetailState.value = IssueDetailState.Error(result.exceptionOrNull()?.message ?: "Failed to load issue")
            }
        }
    }

    fun updateStatus(issueId: Int, newStatus: String) {
        viewModelScope.launch {
            _updateState.value = UpdateState.Loading
            val result = issueRepository.updateIssueStatus(issueId, newStatus)
            if (result.isSuccess) {
                _issue.value = result.getOrNull()
                _updateState.value = UpdateState.Success("Status updated")
            } else {
                _updateState.value = UpdateState.Error(result.exceptionOrNull()?.message ?: "Failed to update status")
            }
        }
    }

    fun addComment(issueId: Int, text: String) {
        viewModelScope.launch {
            _updateState.value = UpdateState.Loading
            val result = issueRepository.addComment(issueId, text)
            if (result.isSuccess) {
                // Reload issue to get updated comments
                loadIssue(issueId)
                _updateState.value = UpdateState.Success("Comment added")
            } else {
                _updateState.value = UpdateState.Error(result.exceptionOrNull()?.message ?: "Failed to add comment")
            }
        }
    }

    sealed class IssueDetailState {
        object Idle : IssueDetailState()
        object Loading : IssueDetailState()
        object Success : IssueDetailState()
        data class Error(val message: String) : IssueDetailState()
    }

    sealed class UpdateState {
        object Idle : UpdateState()
        object Loading : UpdateState()
        data class Success(val message: String) : UpdateState()
        data class Error(val message: String) : UpdateState()
    }
}
