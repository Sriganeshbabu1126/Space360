package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.sgbdevapps.space360.presentation.components.ErrorState
import com.sgbdevapps.space360.presentation.components.IssueCard
import com.sgbdevapps.space360.presentation.components.LoadingState
import com.sgbdevapps.space360.presentation.navigation.Route
import com.sgbdevapps.space360.presentation.viewmodels.DashboardViewModel

@Composable
fun DashboardScreen(
    navController: NavController,
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val sites by viewModel.sites.collectAsState()
    val recentIssues by viewModel.recentIssues.collectAsState()
    val dashboardState by viewModel.dashboardState.collectAsState()

    when (dashboardState) {
        is DashboardViewModel.DashboardState.Loading -> {
            LoadingState()
        }
        is DashboardViewModel.DashboardState.Error -> {
            ErrorState(
                message = (dashboardState as DashboardViewModel.DashboardState.Error).message,
                onRetry = { /* TODO */ }
            )
        }
        else -> {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
            ) {
                item {
                    Text("Assigned Sites", style = MaterialTheme.typography.headlineSmall)
                    Spacer(modifier = Modifier.height(16.dp))
                }
                items(sites) { site ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(8.dp)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(text = site.name, style = MaterialTheme.typography.titleMedium)
                            Text(text = site.location)
                            Text(text = "Open Issues: ${site.openIssuesCount}")
                            Button(
                                onClick = { navController.navigate(Route.IssuesList.route.replace("{siteId}", site.id.toString())) },
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("View Issues")
                            }
                        }
                    }
                }

                item {
                    Spacer(modifier = Modifier.height(32.dp))
                    Text("Recent Issues", style = MaterialTheme.typography.headlineSmall)
                    Spacer(modifier = Modifier.height(16.dp))
                }
                items(recentIssues) { issue ->
                    IssueCard(issue, onClick = {
                        navController.navigate(Route.IssueDetail.route.replace("{issueId}", issue.id.toString()))
                    })
                }
            }
        }
    }
}
