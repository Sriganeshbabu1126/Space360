package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.sgbdevapps.space360.presentation.components.ErrorState
import com.sgbdevapps.space360.presentation.components.IssueCard
import com.sgbdevapps.space360.presentation.components.LoadingState
import com.sgbdevapps.space360.presentation.navigation.Route
import com.sgbdevapps.space360.presentation.viewmodels.IssuesListViewModel

@Composable
fun IssuesListScreen(
    navController: NavController,
    siteId: Int,
    viewModel: IssuesListViewModel = hiltViewModel()
) {
    val filteredIssues by viewModel.filteredIssues.collectAsState()
    val issuesState by viewModel.issuesState.collectAsState()
    val statusFilter by viewModel.statusFilter.collectAsState()

    LaunchedEffect(siteId) {
        viewModel.loadIssuesBySite(siteId)
    }

    val statuses = listOf("Open", "In Review", "Pending", "Closed", "Critical")

    Column(modifier = Modifier.fillMaxSize()) {
        // Filter bar
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("Status Filter:", style = MaterialTheme.typography.labelMedium)
            Box(modifier = Modifier.weight(1f)) {
                // Simple dropdown (Material3)
                var expanded by remember { mutableStateOf(false) }
                Button(onClick = { expanded = true }) {
                    Text(statusFilter ?: "All")
                }
                DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                    DropdownMenuItem(
                        text = { Text("All") },
                        onClick = {
                            viewModel.setStatusFilter(null)
                            expanded = false
                        }
                    )
                    statuses.forEach { status ->
                        DropdownMenuItem(
                            text = { Text(status) },
                            onClick = {
                                viewModel.setStatusFilter(status)
                                expanded = false
                            }
                        )
                    }
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
                    onRetry = { viewModel.loadIssuesBySite(siteId) }
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
                            IssueCard(issue, onClick = {
                                navController.navigate(Route.IssueDetail.route.replace("{issueId}", issue.id.toString()))
                            })
                        }
                    }
                }
            }
        }
    }
}
