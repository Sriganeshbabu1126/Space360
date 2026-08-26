package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.sgbdevapps.space360.presentation.components.LoadingState
import com.sgbdevapps.space360.presentation.components.StatusBadge
import com.sgbdevapps.space360.presentation.viewmodels.IssueDetailViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IssueDetailScreen(
    navController: NavController,
    issueId: Int,
    viewModel: IssueDetailViewModel = hiltViewModel()
) {
    val issue by viewModel.issue.collectAsState()
    val issueDetailState by viewModel.issueDetailState.collectAsState()
    val updateState by viewModel.updateState.collectAsState()
    var newCommentText by remember { mutableStateOf("") }
    var selectedStatus by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(issueId) {
        viewModel.loadIssue(issueId)
    }

    val statuses = listOf("Open", "In Review", "Pending", "Closed", "Critical")

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Issue Detail") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        when (issueDetailState) {
            is IssueDetailViewModel.IssueDetailState.Loading -> {
                LoadingState()
            }
            is IssueDetailViewModel.IssueDetailState.Success -> {
                issue?.let { iss ->
                    LazyColumn(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(innerPadding)
                            .padding(16.dp)
                    ) {
                        item {
                            Text(text = iss.title, style = MaterialTheme.typography.headlineSmall)
                            Spacer(modifier = Modifier.height(8.dp))
                            StatusBadge(iss.status)
                            Spacer(modifier = Modifier.height(16.dp))
                        }

                        item {
                            Text("Description", style = MaterialTheme.typography.labelMedium)
                            Text(iss.description)
                            Spacer(modifier = Modifier.height(16.dp))
                        }

                        item {
                            Text("Priority: ${iss.priority}", style = MaterialTheme.typography.labelMedium)
                            Text("Type: ${iss.type}", style = MaterialTheme.typography.labelMedium)
                            Text("Assigned to: ${iss.assignedToName}", style = MaterialTheme.typography.labelMedium)
                            Spacer(modifier = Modifier.height(16.dp))
                        }

                        // Status update
                        item {
                            Text("Change Status", style = MaterialTheme.typography.labelMedium)
                            var expanded by remember { mutableStateOf(false) }
                            Button(onClick = { expanded = true }, modifier = Modifier.fillMaxWidth()) {
                                Text(selectedStatus ?: iss.status)
                            }
                            DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
                                statuses.forEach { status ->
                                    DropdownMenuItem(
                                        text = { Text(status) },
                                        onClick = {
                                            selectedStatus = status
                                            viewModel.updateStatus(issueId, status)
                                            expanded = false
                                        }
                                    )
                                }
                            }
                            Spacer(modifier = Modifier.height(16.dp))
                        }

                        // Comments
                        item {
                            Text("Comments", style = MaterialTheme.typography.labelMedium)
                        }
                        items(iss.comments) { comment ->
                            Card(modifier = Modifier
                                .fillMaxWidth()
                                .padding(8.dp)) {
                                Column(modifier = Modifier.padding(12.dp)) {
                                    Text(comment.userName, style = MaterialTheme.typography.labelSmall)
                                    Text(comment.text)
                                    Text(comment.createdAt, style = MaterialTheme.typography.labelSmall)
                                }
                            }
                        }

                        // Add comment
                        item {
                            Spacer(modifier = Modifier.height(16.dp))
                            TextField(
                                value = newCommentText,
                                onValueChange = { newCommentText = it },
                                label = { Text("Add comment") },
                                modifier = Modifier.fillMaxWidth()
                            )
                            Button(
                                onClick = { viewModel.addComment(issueId, newCommentText); newCommentText = "" },
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("Submit")
                            }
                        }
                    }
                }
            }
            else -> {}
        }
    }
}
