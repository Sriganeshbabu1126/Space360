package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
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
    siteId: Int,
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
            verticalAlignment = androidx.compose.ui.Alignment.CenterVertically
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
                Icon(Icons.Default.FilterList, contentDescription = "Filters")
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
                    var expanded by remember { mutableStateOf(false) }
                    OutlinedButton(
                        onClick = { expanded = true },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(selectedStatus ?: "Status: All")
                    }
                    DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                        DropdownMenuItem(
                            text = { Text("All Statuses") },
                            onClick = {
                                viewModel.updateStatusFilter(null)
                                expanded = false
                            }
                        )
                        statuses.forEach { status ->
                            DropdownMenuItem(
                                text = { Text(status) },
                                onClick = {
                                    viewModel.updateStatusFilter(status)
                                    expanded = false
                                }
                            )
                        }
                    }
                }

                // Priority Filter
                Box(modifier = Modifier.weight(1f)) {
                    var expanded by remember { mutableStateOf(false) }
                    OutlinedButton(
                        onClick = { expanded = true },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(selectedPriority ?: "Priority: All")
                    }
                    DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                        DropdownMenuItem(
                            text = { Text("All Priorities") },
                            onClick = {
                                viewModel.updatePriorityFilter(null)
                                expanded = false
                            }
                        )
                        priorities.forEach { priority ->
                            DropdownMenuItem(
                                text = { Text(priority) },
                                onClick = {
                                    viewModel.updatePriorityFilter(priority)
                                    expanded = false
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
        when (issuesState) {
            is IssuesListViewModel.IssuesState.Loading -> {
                LoadingState()
            }
            is IssuesListViewModel.IssuesState.Error -> {
                ErrorState(
                    message = (issuesState as IssuesListViewModel.IssuesState.Error).message,
                    onRetry = { viewModel.refreshIssues() }
                )
            }
            else -> {
                if (filteredIssues.isEmpty()) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = androidx.compose.ui.Alignment.Center) {
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
