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
            try {
                Timber.d("PROJECT_FILTER: loading projects")
                
                // Get current user
                val currentUser = authRepository.getCurrentUser().getOrNull()
                    ?: return@launch
                
                Timber.d("PROJECT_FILTER: current user=${currentUser.email} role=${currentUser.role}")
                _userRole.value = currentUser.role
                
                _dashboardState.value = DashboardState.Loading

                // Fetch all projects (sites)
                val sitesResult = siteRepository.getAssignedSites()
                val allProjects = sitesResult.getOrNull() ?: emptyList()
                Timber.d("PROJECT_FILTER: total projects in backend = ${allProjects.size}")

                // Filter by user assignment
                val assignedProjectIds = currentUser.assignedProjectIds ?: emptyList()
                val filteredProjects = allProjects.filter { site ->
                    site.id in assignedProjectIds
                }

                Timber.d("PROJECT_FILTER: assigned projects = ${filteredProjects.size} (ids: $assignedProjectIds)")

                // If user has no assigned projects but is Admin/Manager, show all
                val finalProjects = if (filteredProjects.isEmpty() && 
                    currentUser.role in listOf("Admin", "Manager")) {
                    Timber.d("PROJECT_FILTER: user is Admin/Manager with no assignments — showing all projects")
                    allProjects
                } else {
                    filteredProjects
                }

                _sites.value = finalProjects
                
                // Load recent issues from first site
                if (_sites.value.isNotEmpty()) {
                    val issuesResult = issueRepository.getIssuesBySite(_sites.value[0].id)
                    if (issuesResult.isSuccess) {
                        _recentIssues.value = issuesResult.getOrNull()?.take(5) ?: emptyList()
                    }
                }
                
                _dashboardState.value = DashboardState.Success

            } catch (e: Exception) {
                Timber.e(e, "PROJECT_FILTER: error — ${e.message}")
                _dashboardState.value = DashboardState.Error(e.message ?: "Failed to load sites")
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

