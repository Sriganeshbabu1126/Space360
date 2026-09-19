import os

content = """package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Comment
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.Help
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Sync
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.presentation.viewmodels.IssueViewModel
import com.sgbdevapps.space360.presentation.viewmodels.SyncStatus
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IssuesScreen(
    navController: NavController,
    siteId: String,
    viewModel: IssueViewModel = hiltViewModel()
) {
    val issues by viewModel.issues.collectAsState()
    val selectedSite by viewModel.selectedSite.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val syncBadge by viewModel.syncStatus.collectAsState()
    
    LaunchedEffect(siteId) {
        if (siteId != "all" && siteId.isNotEmpty()) {
            viewModel.selectSite(siteId)
        }
    }

    if (selectedSite == null) {
        // Show project dropdown if no project selected
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("Select Project") },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.primary, titleContentColor = Color.White)
                )
            }
        ) { innerPadding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(16.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("Select a project to view issues", style = MaterialTheme.typography.bodyLarge)
                Spacer(modifier = Modifier.height(16.dp))
                
                val sites by viewModel.sites.collectAsState()
                ProjectDropdown(
                    projects = sites,
                    selectedProject = null,
                    onProjectSelected = { site ->
                        viewModel.selectSite(site.id)
                    }
                )
            }
        }
    } else {
        // Show issues for selected site
        Scaffold(
            topBar = {
                TopAppBar(
                    title = {
                        Column {
                            Text(
                                "Issues",
                                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold)
                            )
                            selectedSite?.let {
                                Text(
                                    "📍 ${it.name}",
                                    style = MaterialTheme.typography.labelSmall.copy(color = Color.LightGray)
                                )
                            }
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.primary,
                        titleContentColor = Color.White
                    )
                )
            },
            floatingActionButton = {
                FloatingActionButton(
                    onClick = { 
                        navController.navigate("create_issue")
                    },
                    containerColor = MaterialTheme.colorScheme.primary,
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Icon(Icons.Filled.Add, contentDescription = "Add Issue", tint = Color.White)
                }
            }
        ) { innerPadding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .background(MaterialTheme.colorScheme.surface)
            ) {
                if (syncBadge != SyncStatus.IDLE) {
                    SyncBadge(status = syncBadge)
                }

                if (isLoading) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
                    }
                } else if (issues.isEmpty()) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                Icons.Filled.CheckCircle,
                                contentDescription = "All caught up",
                                modifier = Modifier.size(64.dp),
                                tint = Color.LightGray
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                "No issues found",
                                style = MaterialTheme.typography.bodyLarge,
                                color = Color.Gray
                            )
                        }
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(issues, key = { it.id }) { issue ->
                            IssueCardEnhanced(
                                issue = issue,
                                onClick = { 
                                    navController.navigate("issue/${issue.id}")
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun SyncBadge(status: SyncStatus) {
    val (color, text, icon) = when (status) {
        SyncStatus.SYNCING -> Triple(Color(0xFF2196F3), "Syncing changes...", Icons.Filled.Sync)
        SyncStatus.SYNCED -> Triple(Color(0xFF4CAF50), "All changes synced", Icons.Filled.CheckCircle)
        SyncStatus.QUEUED -> Triple(Color(0xFFFFC107), "Changes queued for sync", Icons.Filled.Schedule)
        SyncStatus.FAILED -> Triple(Color(0xFFD32F2F), "Sync failed. Will retry.", Icons.Filled.Error)
        SyncStatus.IDLE -> return
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(color.copy(alpha = 0.1f))
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = text,
            tint = color,
            modifier = Modifier.size(16.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text,
            style = MaterialTheme.typography.labelMedium,
            color = color
        )
    }
}

@Composable
fun IssueCardEnhanced(
    issue: Issue,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Text(
                    text = issue.title,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                    modifier = Modifier.weight(1f)
                )
                
                Surface(
                    shape = RoundedCornerShape(4.dp),
                    color = when (issue.status.lowercase()) {
                        "open" -> Color(0xFFD32F2F).copy(alpha = 0.1f)
                        "in review" -> Color(0xFFFFC107).copy(alpha = 0.1f)
                        "closed" -> Color(0xFF4CAF50).copy(alpha = 0.1f)
                        else -> Color.Gray.copy(alpha = 0.1f)
                    },
                    modifier = Modifier.padding(start = 8.dp)
                ) {
                    Text(
                        text = issue.status.uppercase(),
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Bold,
                            color = when (issue.status.lowercase()) {
                                "open" -> Color(0xFFD32F2F)
                                "in review" -> Color(0xFFFF9800)
                                "closed" -> Color(0xFF4CAF50)
                                else -> Color.Gray
                            }
                        )
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = issue.description,
                style = MaterialTheme.typography.bodyMedium,
                color = Color.DarkGray,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                val syncStatusEnum = try {
                    SyncStatus.valueOf(issue.syncStatus ?: "IDLE")
                } catch (e: Exception) {
                    SyncStatus.IDLE
                }
                IssueMetaItem(
                    icon = Icons.Filled.Sync,
                    label = "Sync: " + (issue.syncStatus ?: "IDLE"),
                    color = when (syncStatusEnum) {
                        SyncStatus.QUEUED -> Color(0xFFFF9800)
                        SyncStatus.SYNCING -> Color(0xFF2196F3)
                        SyncStatus.SYNCED -> Color(0xFF4CAF50)
                        SyncStatus.FAILED -> Color(0xFFD32F2F)
                        else -> Color.Gray
                    }
                )
                
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    IssueMetaItem(
                        icon = Icons.Filled.Image,
                        label = issue.photos.size.toString(),
                        color = Color.Gray
                    )
                    IssueMetaItem(
                        icon = Icons.Filled.Comment,
                        label = issue.comments.size.toString(),
                        color = Color.Gray
                    )
                }
            }
        }
    }
}

@Composable
fun IssueMetaItem(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(16.dp), tint = color)
        Spacer(modifier = Modifier.width(4.dp))
        Text(label, style = MaterialTheme.typography.bodySmall, color = color)
    }
}
"""

with open('app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done IssuesScreen")
