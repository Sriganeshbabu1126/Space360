package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.domain.model.Site
import com.sgbdevapps.space360.domain.repository.IssueRepository
import com.sgbdevapps.space360.domain.repository.SiteRepository
import com.sgbdevapps.space360.domain.SessionManager
import com.sgbdevapps.space360.domain.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.SharingStarted
import timber.log.Timber
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val siteRepository: SiteRepository,
    private val issueRepository: IssueRepository,
    private val sessionManager: SessionManager,
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _sites = MutableStateFlow<List<Site>>(emptyList())
    val sites: StateFlow<List<Site>> = _sites

    private val _recentIssues = MutableStateFlow<List<Issue>>(emptyList())
    val recentIssues: StateFlow<List<Issue>> = _recentIssues

    private val _dashboardState = MutableStateFlow<DashboardState>(DashboardState.Idle)
    val dashboardState: StateFlow<DashboardState> = _dashboardState

    private val _selectedSite = MutableStateFlow<Site?>(null)
    val selectedSite: StateFlow<Site?> = _selectedSite

    private val _logoutComplete = MutableStateFlow(false)
    val logoutComplete: StateFlow<Boolean> = _logoutComplete.asStateFlow()

    fun logout() {
        viewModelScope.launch {
            try {
                authRepository.logout()
                _logoutComplete.value = true
            } catch (e: Exception) {
                _logoutComplete.value = true
            }
        }
    }

    fun selectSite(siteId: String) {
        val site = _sites.value.find { it.id == siteId }
        _selectedSite.value = site
        sessionManager.setSelectedSite(site)
    }


    private val _userRole = MutableStateFlow<String>("Manager")
    val userRole: StateFlow<String> = _userRole

    val canCreateProject: StateFlow<Boolean> = _userRole.map { role ->
        val roleStr = role.lowercase().trim()
        Timber.d("ROLE_DEBUG: normalised role = '$roleStr'")
        roleStr in listOf("manager", "supervisor", "360 operator", "360operator", "admin")
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), false)

    init {
        loadDashboard()
    }

    private fun loadDashboard() {
        viewModelScope.launch {
            val user = authRepository.getCurrentUser().getOrNull()
            if (user != null) {
                _userRole.value = user.role
            }
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

