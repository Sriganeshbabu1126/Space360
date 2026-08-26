package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.domain.model.Site
import com.sgbdevapps.space360.domain.repository.IssueRepository
import com.sgbdevapps.space360.domain.repository.SiteRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val siteRepository: SiteRepository,
    private val issueRepository: IssueRepository
) : ViewModel() {

    private val _sites = MutableStateFlow<List<Site>>(emptyList())
    val sites: StateFlow<List<Site>> = _sites

    private val _recentIssues = MutableStateFlow<List<Issue>>(emptyList())
    val recentIssues: StateFlow<List<Issue>> = _recentIssues

    private val _dashboardState = MutableStateFlow<DashboardState>(DashboardState.Idle)
    val dashboardState: StateFlow<DashboardState> = _dashboardState

    init {
        loadDashboard()
    }

    private fun loadDashboard() {
        viewModelScope.launch {
            _dashboardState.value = DashboardState.Loading
            val sitesResult = siteRepository.getAssignedSites()
            if (sitesResult.isSuccess) {
                _sites.value = sitesResult.getOrNull() ?: emptyList()
                // Load recent issues from first site
                if (_sites.value.isNotEmpty()) {
                    val issuesResult = issueRepository.getIssuesBySite(_sites.value[0].id)
                    if (issuesResult.isSuccess) {
                        _recentIssues.value = issuesResult.getOrNull()?.take(5) ?: emptyList()
                    }
                }
                _dashboardState.value = DashboardState.Success
            } else {
                _dashboardState.value = DashboardState.Error(sitesResult.exceptionOrNull()?.message ?: "Failed to load sites")
            }
        }
    }

    sealed class DashboardState {
        object Idle : DashboardState()
        object Loading : DashboardState()
        object Success : DashboardState()
        data class Error(val message: String) : DashboardState()
    }
}
