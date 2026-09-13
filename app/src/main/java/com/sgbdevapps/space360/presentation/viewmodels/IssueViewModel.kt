package com.sgbdevapps.space360.presentation.viewmodels

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.data.remote.IssuesService
import com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.domain.model.Site
import com.sgbdevapps.space360.service.OfflineSyncManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import com.sgbdevapps.space360.data.remote.AddCommentRequest
import javax.inject.Inject
import com.sgbdevapps.space360.domain.repository.SiteRepository
import com.sgbdevapps.space360.domain.SessionManager

enum class SyncStatus {
    IDLE, SYNCING, SYNCED, QUEUED, FAILED
}

@HiltViewModel
class IssueViewModel @Inject constructor(
    private val api: IssuesService,
    private val offlineSyncManager: OfflineSyncManager,
    private val siteRepository: SiteRepository,
    private val sessionManager: SessionManager
) : ViewModel() {
    
    private val TAG = "IssueViewModel"

    init {
        viewModelScope.launch {
            try {
                val result = siteRepository.getAssignedSites()
                if (result.isSuccess) {
                    _sites.value = result.getOrNull() ?: emptyList()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error loading sites", e)
            }
            
            sessionManager.selectedSite.collect { site ->
                _selectedSite.value = site
                site?.let { loadIssues(it.id) }
            }
        }
    }

    
    private val _issues = MutableStateFlow<List<Issue>>(emptyList())
    val issues = _issues.asStateFlow()
    
    private val _syncStatus = MutableStateFlow(SyncStatus.IDLE)
    val syncStatus = _syncStatus.asStateFlow()
    
    private val _selectedSite = MutableStateFlow<Site?>(null)
    val selectedSite = _selectedSite.asStateFlow()

    private val _sites = MutableStateFlow<List<Site>>(emptyList())
    val sites = _sites.asStateFlow()
    
    fun selectSite(siteId: String) {
        // Find the site or create a dummy one if sites aren't loaded here
        val site = _sites.value.find { it.id == siteId } 
                   ?: Site(id = siteId, name = "Project $siteId")
        _selectedSite.value = site
        loadIssues(siteId)
    }

    
    private val _isLoading = MutableStateFlow(false)
    val isLoading = _isLoading.asStateFlow()
    
    fun loadIssues(siteId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val issuesList = api.getIssuesBySite(siteId = siteId)
                val mapped = issuesList.map { 
                    var finalStatus = it.status
                    try {
                        val pending = offlineSyncManager.getPendingItemsForResource("issue", it.id)
                        pending.forEach { action ->
                            if (action.operationType == "update_status") {
                                try {
                                    val req = Json.decodeFromString<UpdateIssueStatusRequest>(action.payload)
                                    finalStatus = req.status
                                } catch(e:Exception){}
                            }
                        }
                    } catch(e:Exception){}
                
                    Issue(
                        id = it.id,
                        title = it.title,
                        description = it.description ?: "",
                        status = finalStatus,
                        priority = it.priority ?: "",
                        siteId = it.site_id ?: "",
                        assignedTo = "",
                        assignedToName = "",
                        createdAt = it.created_at ?: "",
                        updatedAt = it.updated_at ?: "",
                        comments = emptyList() // simplified
                    )
                }
                _issues.value = mapped
            } catch (e: Exception) {
                Log.e(TAG, "Failed to load issues", e)
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun updateIssueStatus(issueId: String, newStatus: String) {
        viewModelScope.launch {
            try {
                _syncStatus.value = SyncStatus.SYNCING
                api.updateIssueStatus(issueId, UpdateIssueStatusRequest(newStatus))
                _issues.value = _issues.value.map {
                    if (it.id == issueId) it.copy(status = newStatus) else it
                }
                _syncStatus.value = SyncStatus.SYNCED
            } catch (e: Exception) {
                Log.e(TAG, "Failed to update status", e)
                offlineSyncManager.queueAction(
                    action = "update_status",
                    resourceType = "issue",
                    resourceId = issueId,
                    payload = UpdateIssueStatusRequest(newStatus)
                )
                _syncStatus.value = SyncStatus.QUEUED
                
                // Optimistic UI update
                _issues.value = _issues.value.map {
                    if (it.id == issueId) it.copy(status = newStatus) else it
                }
            }
        }
    }
}
