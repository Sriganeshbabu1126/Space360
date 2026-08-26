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
class IssuesListViewModel @Inject constructor(
    private val issueRepository: IssueRepository
) : ViewModel() {

    private val _issues = MutableStateFlow<List<Issue>>(emptyList())
    val issues: StateFlow<List<Issue>> = _issues

    private val _filteredIssues = MutableStateFlow<List<Issue>>(emptyList())
    val filteredIssues: StateFlow<List<Issue>> = _filteredIssues

    private val _selectedSiteId = MutableStateFlow<Int?>(null)
    val selectedSiteId: StateFlow<Int?> = _selectedSiteId

    private val _statusFilter = MutableStateFlow<String?>(null)
    val statusFilter: StateFlow<String?> = _statusFilter

    private val _issuesState = MutableStateFlow<IssuesState>(IssuesState.Idle)
    val issuesState: StateFlow<IssuesState> = _issuesState

    fun loadIssuesBySite(siteId: Int) {
        _selectedSiteId.value = siteId
        viewModelScope.launch {
            _issuesState.value = IssuesState.Loading
            val result = issueRepository.getIssuesBySite(siteId)
            if (result.isSuccess) {
                _issues.value = result.getOrNull() ?: emptyList()
                applyFilters()
                _issuesState.value = IssuesState.Success
            } else {
                _issuesState.value = IssuesState.Error(result.exceptionOrNull()?.message ?: "Failed to load issues")
            }
        }
    }

    fun setStatusFilter(status: String?) {
        _statusFilter.value = status
        applyFilters()
    }

    private fun applyFilters() {
        var filtered = _issues.value
        _statusFilter.value?.let { status ->
            filtered = filtered.filter { it.status == status }
        }
        _filteredIssues.value = filtered
    }

    sealed class IssuesState {
        object Idle : IssuesState()
        object Loading : IssuesState()
        object Success : IssuesState()
        data class Error(val message: String) : IssuesState()
    }
}
