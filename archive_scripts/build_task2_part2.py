import os

ISSUES_SCREEN_PATH = r"F:\Space360\app\src\main\java\com\sgbdevapps\space360\presentation\screens\IssuesScreen.kt"

ISSUES_CONTENT = """package com.sgbdevapps.space360.presentation.screens

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
import com.sgbdevapps.space360.service.SyncStatus

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IssuesScreen(
    viewModel: IssueViewModel = hiltViewModel(),
    onIssueClick: (String) -> Unit
) {
    val issues by viewModel.issues.collectAsState()
    val selectedSite by viewModel.selectedSite.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val syncBadge by viewModel.syncStatus.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            "Issues",
                            style = MaterialTheme.typography.headlineSmall.copy(
                                fontWeight = FontWeight.Bold
                            )
                        )
                        selectedSite?.let {
                            Text(
                                "📍 ${it.name}",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    color = Color.Gray
                                )
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.White,
                    titleContentColor = Color.Black
                )
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { /* Navigate to create issue */ },
                containerColor = Color(0xFF1D9E75),
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
        ) {
            // Sync Status Banner
            if (syncBadge == SyncStatus.SYNCING) {
                Surface(
                    color = Color(0xFF2196F3).copy(alpha = 0.1f),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            strokeWidth = 2.dp,
                            color = Color(0xFF2196F3)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            "Syncing changes...",
                            style = MaterialTheme.typography.bodySmall.copy(
                                color = Color(0xFF2196F3)
                            )
                        )
                    }
                }
            }
            
            // Issues List
            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        CircularProgressIndicator()
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Loading issues...")
                    }
                }
            } else if (issues.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            Icons.Filled.CheckCircle,
                            contentDescription = "No issues",
                            tint = Color.Gray,
                            modifier = Modifier.size(48.dp)
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            "No issues to show",
                            style = MaterialTheme.typography.bodyLarge
                        )
                        Text(
                            "Create a new issue or check another site",
                            style = MaterialTheme.typography.bodySmall.copy(
                                color = Color.Gray
                            )
                        )
                    }
                }
            } else {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(issues) { issue ->
                        IssueCardEnhanced(
                            issue = issue,
                            onClick = { onIssueClick(issue.id) },
                            onQuickAction = { action ->
                                viewModel.updateIssueStatus(issue.id, action)
                            }
                        )
                    }
                    
                    // Bottom padding for FAB
                    item {
                        Spacer(modifier = Modifier.height(80.dp))
                    }
                }
            }
        }
    }
}

@Composable
fun IssueCardEnhanced(
    issue: Issue,
    onClick: () -> Unit,
    onQuickAction: (String) -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(8.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, Color(0xFFEEEEEE))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            
            // Top Row: Priority + Title + Sync Status
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.Top,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                // Priority Badge + Title
                Column(modifier = Modifier.weight(1f)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // Priority Badge
                        Surface(
                            color = when (issue.priority) {
                                "high" -> Color(0xFFD32F2F)
                                "medium" -> Color(0xFFFFC107)
                                else -> Color(0xFF4CAF50)
                            },
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Text(
                                issue.priority.uppercase(),
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                ),
                                modifier = Modifier.padding(4.dp, 2.dp)
                            )
                        }
                        
                        // Title
                        Text(
                            issue.title,
                            style = MaterialTheme.typography.bodyLarge.copy(
                                fontWeight = FontWeight.Bold,
                                color = Color.Black
                            ),
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                }
                
                // Sync Status
                SyncBadge(issue.syncStatus)
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Description
            Text(
                issue.description,
                style = MaterialTheme.typography.bodySmall.copy(
                    color = Color(0xFF666666)
                ),
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Metadata Row: Comments, Photos, Status
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    modifier = Modifier.weight(1f)
                ) {
                    // Comments
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            Icons.Filled.Comment,
                            contentDescription = "Comments",
                            tint = Color.Gray,
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            "${issue.comments.size}",
                            style = MaterialTheme.typography.labelSmall.copy(
                                color = Color.Gray
                            )
                        )
                    }
                    
                    // Photos
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            Icons.Filled.Image,
                            contentDescription = "Photos",
                            tint = Color.Gray,
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            "${issue.photos.size}",
                            style = MaterialTheme.typography.labelSmall.copy(
                                color = Color.Gray
                            )
                        )
                    }
                }
                
                // Status Chip
                Surface(
                    color = when (issue.status) {
                        "open" -> Color(0xFFE3F2FD)
                        "in_review" -> Color(0xFFFFF3E0)
                        "closed" -> Color(0xFFE8F5E9)
                        else -> Color(0xFFF5F5F5)
                    },
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        issue.status.replace("_", " ").uppercase(),
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Bold,
                            color = when (issue.status) {
                                "open" -> Color(0xFF1976D2)
                                "in_review" -> Color(0xFFF57C00)
                                "closed" -> Color(0xFF388E3C)
                                else -> Color.Gray
                            }
                        ),
                        modifier = Modifier.padding(8.dp, 4.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun SyncBadge(status: SyncStatus) {
    val (color, icon, label) = when (status) {
        SyncStatus.SYNCING -> Triple(
            Color(0xFF2196F3),
            Icons.Filled.Sync,
            "Syncing"
        )
        SyncStatus.SYNCED -> Triple(
            Color(0xFF4CAF50),
            Icons.Filled.CheckCircle,
            "Synced"
        )
        SyncStatus.QUEUED -> Triple(
            Color(0xFFFFC107),
            Icons.Filled.Schedule,
            "Queued"
        )
        SyncStatus.FAILED -> Triple(
            Color(0xFFD32F2F),
            Icons.Filled.Error,
            "Failed"
        )
        else -> Triple(
            Color.Gray,
            Icons.Filled.Help,
            "Unknown"
        )
    }
    
    Surface(
        color = color.copy(alpha = 0.1f),
        shape = RoundedCornerShape(8.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            modifier = Modifier.padding(6.dp, 4.dp)
        ) {
            if (status == SyncStatus.SYNCING) {
                // Animated rotation for syncing icon
                Box(
                    modifier = Modifier
                        .size(14.dp)
                        .graphicsLayer {
                            rotationZ = (System.currentTimeMillis() % 2000) / 2000f * 360f
                        }
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = label,
                        tint = color,
                        modifier = Modifier.size(14.dp)
                    )
                }
            } else {
                Icon(
                    imageVector = icon,
                    contentDescription = label,
                    tint = color,
                    modifier = Modifier.size(14.dp)
                )
            }
            
            Text(
                label,
                style = MaterialTheme.typography.labelSmall.copy(
                    fontWeight = FontWeight.Bold,
                    color = color,
                    fontSize = 11.sp
                )
            )
        }
    }
}
"""

with open(ISSUES_SCREEN_PATH, "w", encoding="utf-8") as f:
    f.write(ISSUES_CONTENT)
print("Updated IssuesScreen.kt")
