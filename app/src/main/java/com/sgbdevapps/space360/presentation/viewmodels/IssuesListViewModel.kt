package com.sgbdevapps.space360.presentation.viewmodels

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.data.network.NetworkConnectivityManager
import com.sgbdevapps.space360.data.sync.SyncWorker
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.domain.repository.IssueRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class IssuesListViewModel @Inject constructor(
    private val issueRepository: IssueRepository,
    private val networkConnectivity: NetworkConnectivityManager,
    @ApplicationContext private val context: Context
) : ViewModel() {

    private val _isOnline = MutableStateFlow(true)
    val isOnline: StateFlow<Boolean> = _isOnline

    private val _pendingSyncCount = MutableStateFlow(0)
    val pendingSyncCount: StateFlow<Int> = _pendingSyncCount

    private val _issues = MutableStateFlow<List<Issue>>(emptyList())
    val issues: StateFlow<List<Issue>> = _issues

    private val _selectedSiteId = MutableStateFlow<String?>(null)
    val selectedSiteId: StateFlow<String?> = _selectedSiteId

    private val _selectedStatusFilter = MutableStateFlow<String?>(null)
    val selectedStatusFilter: StateFlow<String?> = _selectedStatusFilter.asStateFlow()

    private val _selectedSiteFilter = MutableStateFlow<String?>(null)
    val selectedSiteFilter: StateFlow<String?> = _selectedSiteFilter.asStateFlow()

    private val _selectedPriorityFilter = MutableStateFlow<String?>(null)
    val selectedPriorityFilter: StateFlow<String?> = _selectedPriorityFilter.asStateFlow()

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val filteredIssues: StateFlow<List<Issue>> = combine(
        issues,
        selectedStatusFilter,
        selectedSiteFilter,
        selectedPriorityFilter,
        searchQuery
    ) { allIssues, status, site, priority, query ->
        allIssues.filter { issue ->
            (status == null || issue.status == status) &&
            (priority == null || issue.priority == priority) &&
            (query.isEmpty() || issue.title.contains(query, ignoreCase = true) || 
             issue.description.contains(query, ignoreCase = true))
        }
    }.stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    private val _issuesState = MutableStateFlow<IssuesState>(IssuesState.Idle)
    val issuesState: StateFlow<IssuesState> = _issuesState

    init {
        viewModelScope.launch {
            networkConnectivity.isOnline.collectLatest { online ->
                _isOnline.value = online
                if (online) {
                    SyncWorker.triggerImmediateSyncOnConnectivity(context)
                }
            }
        }

        viewModelScope.launch {
            issueRepository.observePendingSyncCount().collectLatest { count ->
                _pendingSyncCount.value = count
            }
        }
    }

    fun loadIssuesBySite(siteId: String, forceRefresh: Boolean = false) {
        _selectedSiteId.value = siteId
        _selectedSiteFilter.value = siteId
        viewModelScope.launch {
            _issuesState.value = IssuesState.Loading
            val result = issueRepository.getIssuesBySite(siteId, forceRefresh)
            if (result.isSuccess) {
                _issues.value = result.getOrNull() ?: emptyList()
                _issuesState.value = IssuesState.Success
            } else {
                _issuesState.value = IssuesState.Error(result.exceptionOrNull()?.message ?: "Failed to load issues")
            }
        }
    }

    fun updateStatusFilter(status: String?) {
        _selectedStatusFilter.value = status
    }

    fun updateSiteFilter(site: String?) {
        _selectedSiteFilter.value = site
    }

    fun updatePriorityFilter(priority: String?) {
        _selectedPriorityFilter.value = priority
    }

    fun updateSearchQuery(query: String) {
        _searchQuery.value = query
    }

    fun refreshIssues() {
        val siteId = _selectedSiteId.value ?: return
        viewModelScope.launch {
            loadIssuesBySite(siteId, forceRefresh = true)
        }
    }

    fun retrySync() {
        SyncWorker.triggerImmediateSyncOnConnectivity(context)
    }

    sealed class IssuesState {
        object Idle : IssuesState()
        object Loading : IssuesState()
        object Success : IssuesState()
        data class Error(val message: String) : IssuesState()
    }
}
