import os

content = """package com.sgbdevapps.space360.presentation.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.PhotoCamera
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.FileProvider
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import coil.compose.AsyncImage
import com.sgbdevapps.space360.domain.model.IssueComment
import com.sgbdevapps.space360.domain.model.IssuePhoto
import com.sgbdevapps.space360.presentation.viewmodels.IssueDetailViewModel
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IssueDetailScreen(
    navController: NavController,
    issueId: String,
    viewModel: IssueDetailViewModel = hiltViewModel()
) {
    val issue by viewModel.issue.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()
    val context = LocalContext.current
    
    var photoUri by remember { mutableStateOf<Uri?>(null) }
    
    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture()
    ) { success ->
        if (success && photoUri != null) {
            val result = com.sgbdevapps.space360.utils.PhotoCompressionHelper.compressPhotoIfNeeded(context, photoUri!!)
            if (result.success) {
                android.widget.Toast.makeText(context, "Compressed successfully", android.widget.Toast.LENGTH_SHORT).show()
                viewModel.uploadPhotoUri(Uri.parse("file://${result.compressedFilePath}"))
            } else {
                android.widget.Toast.makeText(context, "Failed to compress", android.widget.Toast.LENGTH_LONG).show()
            }
        }
    }

    val cameraPermissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            val tempFile = File.createTempFile("capture_", ".jpg", context.cacheDir)
            photoUri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                tempFile
            )
            cameraLauncher.launch(photoUri!!)
        } else {
            android.widget.Toast.makeText(context, "Camera permission denied", android.widget.Toast.LENGTH_SHORT).show()
        }
    }

    LaunchedEffect(issueId) {
        viewModel.loadIssue(issueId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(issue?.title ?: "Loading...") },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.primary, titleContentColor = Color.White)
            )
        }
    ) { innerPadding ->
        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else if (error != null) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("Error: $error")
            }
        } else if (issue != null) {
            val currentIssue = issue!!
            Column(
                modifier = Modifier
                    .padding(innerPadding)
                    .padding(16.dp)
            ) {
                // Issue Status Editable
                IssueStatusSelector(
                    currentStatus = currentIssue.status,
                    onStatusChange = { newStatus ->
                        viewModel.updateIssueStatus(newStatus)
                    }
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                Text(currentIssue.description, style = MaterialTheme.typography.bodyLarge)
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Photos Section
                PhotosSection(
                    photos = currentIssue.photos,
                    onAddPhoto = { cameraPermissionLauncher.launch(android.Manifest.permission.CAMERA) }
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Comments Section
                CommentsSection(
                    comments = currentIssue.comments,
                    onAddComment = { text -> viewModel.addComment(text) },
                    isLoading = isLoading
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IssueStatusSelector(
    currentStatus: String,
    onStatusChange: (String) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    val statuses = listOf("Open", "In Review", "Closed")
    
    ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = !expanded }) {
        OutlinedTextField(
            value = currentStatus,
            onValueChange = {},
            readOnly = true,
            label = { Text("Status") },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier = Modifier.menuAnchor().fillMaxWidth()
        )
        
        ExposedDropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            statuses.forEach { status ->
                DropdownMenuItem(
                    text = { Text(status) },
                    onClick = {
                        onStatusChange(status)
                        expanded = false
                    }
                )
            }
        }
    }
}

@Composable
fun PhotosSection(
    photos: List<IssuePhoto>,
    onAddPhoto: () -> Unit
) {
    Column(modifier = Modifier.fillMaxWidth().heightIn(min = 100.dp, max = 250.dp)) {
        Text("Photos (${photos.size})", style = MaterialTheme.typography.headlineSmall)
        
        if (photos.isEmpty()) {
            Text("No photos yet", style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray))
        } else {
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth().weight(1f).padding(vertical = 8.dp)
            ) {
                items(photos) { photo ->
                    PhotoCard(photo)
                }
            }
        }
        
        Button(
            onClick = onAddPhoto,
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp)
        ) {
            Icon(Icons.Filled.PhotoCamera, contentDescription = "Add Photo")
            Spacer(modifier = Modifier.width(8.dp))
            Text("Add Photo")
        }
    }
}

@Composable
fun PhotoCard(photo: IssuePhoto) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(1f),
        shape = RoundedCornerShape(8.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        if (photo.photoUrl.isNotEmpty()) {
            AsyncImage(
                model = photo.photoUrl,
                contentDescription = "Issue photo",
                contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize()
            )
        } else {
            Box(
                modifier = Modifier.fillMaxSize().background(Color.Gray),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Filled.Image, contentDescription = "Photo", tint = Color.White, modifier = Modifier.size(48.dp))
            }
        }
    }
}

@Composable
fun CommentsSection(
    comments: List<IssueComment>,
    onAddComment: (String) -> Unit,
    isLoading: Boolean
) {
    var newComment by remember { mutableStateOf("") }
    
    Column(modifier = Modifier.fillMaxWidth()) {
        Text("Comments (${comments.size})", style = MaterialTheme.typography.headlineSmall)
        
        // Existing comments
        comments.forEach { comment ->
            CommentCard(comment)
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Add comment input
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = newComment,
                onValueChange = { newComment = it },
                placeholder = { Text("Add a comment...") },
                modifier = Modifier.weight(1f)
            )
            
            Button(
                onClick = {
                    if (newComment.isNotBlank()) {
                        onAddComment(newComment)
                        newComment = ""
                    }
                },
                enabled = newComment.isNotBlank() && !isLoading
            ) {
                Text("Post")
            }
        }
    }
}

@Composable
fun CommentCard(comment: IssueComment) {
    Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(comment.userName, style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Bold))
            Text(comment.text, style = MaterialTheme.typography.bodyMedium)
            Text(comment.createdAt, style = MaterialTheme.typography.labelSmall.copy(color = Color.Gray))
        }
    }
}
"""

with open('app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
