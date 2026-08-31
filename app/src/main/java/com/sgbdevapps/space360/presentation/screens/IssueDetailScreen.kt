package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.sgbdevapps.space360.presentation.components.*
import com.sgbdevapps.space360.presentation.viewmodels.IssueDetailViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IssueDetailScreen(
    navController: NavController,
    issueId: String,
    viewModel: IssueDetailViewModel = hiltViewModel()
) {
    val issue by viewModel.issue.collectAsState()
    val isAdmin by viewModel.isAdmin.collectAsState()
    val comments by viewModel.comments.collectAsState()
    val photos by viewModel.photos.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val isOnline by viewModel.isOnline.collectAsState()
    val lastCacheUpdateTime by viewModel.lastCacheUpdateTime.collectAsState()

    var showStatusBottomSheet by remember { mutableStateOf(false) }
    var selectedPhotoIndex by remember { mutableStateOf<Int?>(null) }

    LaunchedEffect(issueId) {
        viewModel.loadIssueDetail(issueId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Issue Details") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { /* Menu */ }) {
                        Icon(Icons.Default.MoreVert, contentDescription = "Menu")
                    }
                }
            )
        },
        bottomBar = {
            CommentInputField(
                isOnline = isOnline,
                onSendComment = { text -> viewModel.addComment(issueId, text) }
            )
        }
    ) { padding ->
        if (isLoading && issue == null) {
            Box(modifier = Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else if (issue != null) {
            val currentIssue = issue!!
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(horizontal = 16.dp)
                    .verticalScroll(rememberScrollState())
            ) {
                if (!isOnline && lastCacheUpdateTime != null) {
                    Text(
                        text = "Cached data",
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.labelSmall
                    )
                }

                Text(text = currentIssue.title, fontWeight = FontWeight.Bold, fontSize = 22.sp)
                Spacer(modifier = Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("Site: ${currentIssue.siteId} | Priority: ${currentIssue.priority}", fontSize = 14.sp)
                    Spacer(modifier = Modifier.weight(1f))
                    StatusBadge(currentIssue.status)
                }
                Spacer(modifier = Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("Created: ${currentIssue.createdAt}", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    if (currentIssue.syncStatus != null) {
                        Spacer(modifier = Modifier.width(8.dp))
                        IssueSyncStatusBadge(syncStatus = currentIssue.syncStatus)
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Button(
                    onClick = { showStatusBottomSheet = true },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Update Status")
                }

                Spacer(modifier = Modifier.height(16.dp))
                Text("Description", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                Spacer(modifier = Modifier.height(4.dp))
                Text(text = currentIssue.description, fontSize = 16.sp)

                Spacer(modifier = Modifier.height(16.dp))
                HorizontalDivider()

                PhotoGallery(
                    photos = photos,
                    isOnline = isOnline,
                    onAddPhotos = { paths -> viewModel.addPhotos(issueId, paths) },
                    onPhotoClick = { index -> selectedPhotoIndex = index }
                )

                HorizontalDivider()
                Spacer(modifier = Modifier.height(8.dp))

                CommentThread(comments = comments)
                
                Spacer(modifier = Modifier.height(100.dp)) // Padding for bottom input
            }

            if (showStatusBottomSheet) {
                StatusUpdateBottomSheet(
                    currentStatus = currentIssue.status,
                    isAdmin = isAdmin,
                    onUpdateStatus = { newStatus -> viewModel.updateIssueStatus(issueId, newStatus) },
                    onDismiss = { showStatusBottomSheet = false }
                )
            }

            if (selectedPhotoIndex != null) {
                PhotoLightbox(
                    photos = photos,
                    initialIndex = selectedPhotoIndex!!,
                    onDismiss = { selectedPhotoIndex = null }
                )
            }
        }
    }
}
