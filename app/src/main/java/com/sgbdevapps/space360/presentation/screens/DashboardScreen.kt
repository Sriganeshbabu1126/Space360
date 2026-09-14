package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExitToApp
import androidx.compose.material.icons.filled.AddCircleOutline
import androidx.compose.ui.text.font.FontWeight
import com.sgbdevapps.space360.presentation.viewmodels.AuthViewModel
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.sgbdevapps.space360.domain.model.Site
import com.sgbdevapps.space360.presentation.navigation.Route
import com.sgbdevapps.space360.presentation.viewmodels.DashboardViewModel
import com.sgbdevapps.space360.presentation.components.LoadingState
import com.sgbdevapps.space360.presentation.components.ErrorState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    navController: NavController,
    onLogout: () -> Unit = {},
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val sites by viewModel.sites.collectAsState()
    val selectedSite by viewModel.selectedSite.collectAsState()
    val userRole by viewModel.userRole.collectAsState()
    val dashboardState by viewModel.dashboardState.collectAsState()
    val logoutComplete by viewModel.logoutComplete.collectAsState()
    val canCreateProject by viewModel.canCreateProject.collectAsState()

    LaunchedEffect(logoutComplete) {
        if (logoutComplete) {
            onLogout()
        }
    }

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
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "Space360 Dashboard",
                        style = MaterialTheme.typography.headlineMedium
                    )
                    IconButton(onClick = { viewModel.logout() }) {
                        Icon(Icons.Filled.ExitToApp, contentDescription = "Logout")
                    }
                }
                Spacer(modifier = Modifier.height(16.dp))
                Text("Select your project", style = MaterialTheme.typography.headlineSmall)
                Spacer(modifier = Modifier.height(16.dp))
                
                // Project Dropdown
                ProjectDropdown(
                    projects = sites,
                    selectedProject = selectedSite,
                    onProjectSelected = { project ->
                        viewModel.selectSite(project.id)
                    }
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Show stats for selected site
                selectedSite?.let { site ->
                    SiteStatsCard(site)
                    
                    Spacer(modifier = Modifier.height(24.dp))
                    
                    // Quick Actions
                    Button(
                        onClick = { navController.navigate(Route.IssuesList.route.replace("{siteId}", site.id)) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("View Issues")
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProjectDropdown(
    projects: List<Site>,
    selectedProject: Site?,
    onProjectSelected: (Site) -> Unit,
    canCreateProject: Boolean = false
) {
    var expanded by remember { mutableStateOf(false) }
    
    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = !expanded }
    ) {
        OutlinedTextField(
            value = selectedProject?.name ?: "Select your project",
            onValueChange = {},
            readOnly = true,
            label = { Text("Project") },
            trailingIcon = {
                ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded)
            },
            modifier = Modifier
                .fillMaxWidth()
                .menuAnchor()
        )
        
        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            projects.forEach { project ->
                DropdownMenuItem(
                    text = { Text(project.name) },
                    onClick = {
                        onProjectSelected(project)
                        expanded = false
                    }
                )
            }
            if (canCreateProject) {
                HorizontalDivider()
                DropdownMenuItem(
                    text = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Default.AddCircleOutline,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                "Create New Project",
                                color = MaterialTheme.colorScheme.primary,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    },
                    onClick = {
                        // TODO: Navigate to create project screen
                        expanded = false
                    }
                )
            }
        }
    }
}

@Composable
fun SiteStatsCard(site: Site) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = site.name, style = MaterialTheme.typography.titleLarge)
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = site.location ?: "Location not specified", style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = "Open Issues: ${site.openIssuesCount}", style = MaterialTheme.typography.bodyLarge, color = MaterialTheme.colorScheme.error)
            Spacer(modifier = Modifier.height(4.dp))
            Text(text = "Status: ${site.status}", style = MaterialTheme.typography.bodyMedium)
        }
    }
}
