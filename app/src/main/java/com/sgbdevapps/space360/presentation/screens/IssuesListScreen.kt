package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.List
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.presentation.components.ErrorState
import com.sgbdevapps.space360.presentation.components.IssueCard
import com.sgbdevapps.space360.presentation.components.LoadingState
import com.sgbdevapps.space360.presentation.components.OfflineBanner
import com.sgbdevapps.space360.presentation.navigation.Route
import com.sgbdevapps.space360.presentation.viewmodels.IssuesListViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IssuesListScreen(
    navController: NavController,
    siteId: String,
    viewModel: IssuesListViewModel = hiltViewModel()
) {
    val filteredIssues by viewModel.filteredIssues.collectAsState()
    val issuesState by viewModel.issuesState.collectAsState()
    val isOnline by viewModel.isOnline.collectAsState()
    val pendingSyncCount by viewModel.pendingSyncCount.collectAsState()
    
    val searchQuery by viewModel.searchQuery.collectAsState()
    val selectedStatus by viewModel.selectedStatusFilter.collectAsState()
    val selectedPriority by viewModel.selectedPriorityFilter.collectAsState()

    var showFilters by remember { mutableStateOf(false) }

    LaunchedEffect(siteId) {
        viewModel.loadIssuesBySite(siteId)
    }

    val statuses = listOf("Open", "In Progress", "Done", "Closed")
    val priorities = listOf("High", "Medium", "Low")

    Column(modifier = Modifier.fillMaxSize()) {
        OfflineBanner(isOnline = isOnline, pendingSyncCount = pendingSyncCount)
        
        // Search Bar and Filter Toggle
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { viewModel.updateSearchQuery(it) },
                modifier = Modifier.weight(1f),
                placeholder = { Text("Search issues...") },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Search") },
                singleLine = true
            )
            Spacer(modifier = Modifier.width(8.dp))
            IconButton(onClick = { showFilters = !showFilters }) {
                Icon(Icons.Default.List, contentDescription = "Filters")
            }
        }

        // Inline Filters
        if (showFilters) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Status Filter
                Box(modifier = Modifier.weight(1f)) {
                    var statusExpanded by remember { mutableStateOf(false) }
                    OutlinedButton(
                        onClick = { statusExpanded = true },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(selectedStatus ?: "Status: All")
                    }
                    DropdownMenu(expanded = statusExpanded, onDismissRequest = { statusExpanded = false }) {
                        DropdownMenuItem(
                            text = { Text("All Statuses") },
                            onClick = {
                                viewModel.updateStatusFilter(null)
                                statusExpanded = false
                            }
                        )
                        statuses.forEach { status ->
                            DropdownMenuItem(
                                text = { Text(status) },
                                onClick = {
                                    viewModel.updateStatusFilter(status)
                                    statusExpanded = false
                                }
                            )
                        }
                    }
                }

                // Priority Filter
                Box(modifier = Modifier.weight(1f)) {
                    var priorityExpanded by remember { mutableStateOf(false) }
                    OutlinedButton(
                        onClick = { priorityExpanded = true },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(selectedPriority ?: "Priority: All")
                    }
                    DropdownMenu(expanded = priorityExpanded, onDismissRequest = { priorityExpanded = false }) {
                        DropdownMenuItem(
                            text = { Text("All Priorities") },
                            onClick = {
                                viewModel.updatePriorityFilter(null)
                                priorityExpanded = false
                            }
                        )
                        priorities.forEach { priority ->
                            DropdownMenuItem(
                                text = { Text(priority) },
                                onClick = {
                                    viewModel.updatePriorityFilter(priority)
                                    priorityExpanded = false
                                }
                            )
                        }
                    }
                }
            }
        }

        // Pull to refresh layout can be wrapped here, but for simplicity we'll just have a button or rely on LoadingState
        // To implement PullRefresh we need material pullrefresh which is in compose material (not material3 yet, or uses accompanist)
        // Let's add a manual refresh button if online
        if (isOnline) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center
            ) {
                TextButton(onClick = { viewModel.refreshIssues() }) {
                    Text("Refresh Data")
                }
            }
        }

        // Issues list
        when (val state = issuesState) {
            is IssuesListViewModel.IssuesState.Loading -> {
                LoadingState()
            }
            is IssuesListViewModel.IssuesState.Error -> {
                ErrorState(
                    message = state.message,
                    onRetry = { viewModel.refreshIssues() }
                )
            }
            else -> {
                if (filteredIssues.isEmpty()) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("No issues found")
                    }
                } else {
                    LazyColumn(modifier = Modifier.fillMaxSize()) {
                        items(filteredIssues) { issue ->
                            IssueCard(
                                issue = issue,
                                onRetrySync = { viewModel.retrySync() },
                                onClick = {
                                    navController.navigate(Route.IssueDetail.route.replace("{issueId}", issue.id.toString()))
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}
