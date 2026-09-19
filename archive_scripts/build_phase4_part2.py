import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path}")

# IssueDetailScreen.kt
write_file("app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt", """
package com.sgbdevapps.space360.presentation.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.sgbdevapps.space360.presentation.viewmodels.IssueDetailViewModel
import androidx.navigation.NavController
import com.sgbdevapps.space360.presentation.components.CommentThread
import com.sgbdevapps.space360.presentation.components.PhotoGallery
import com.sgbdevapps.space360.presentation.components.StatusBadge
import com.sgbdevapps.space360.presentation.components.CommentInputField
import kotlinx.coroutines.launch

@Composable
fun IssueDetailScreen(
    navController: NavController,
    issueId: String,
    viewModel: IssueDetailViewModel = hiltViewModel()
) {
    val issue by viewModel.issue.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()
    val scope = rememberCoroutineScope()
    
    // Camera launcher
    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicturePreview()
    ) { bitmap ->
        bitmap?.let {
            viewModel.uploadPhotoBitmap(it)
        }
    }
    
    // Gallery launcher
    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            viewModel.uploadPhotoUri(it)
        }
    }

    LaunchedEffect(issueId) {
        viewModel.loadIssue(issueId)
    }

    if (isLoading) {
        CircularProgressIndicator()
    } else if (error != null) {
        Text("Error: $error")
    } else if (issue != null) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(issue!!.title, style = MaterialTheme.typography.headlineMedium)
            StatusBadge(issue!!.status)
            Spacer(modifier = Modifier.height(8.dp))
            Text(issue!!.description)
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                Button(onClick = { cameraLauncher.launch(null) }) {
                    Text("Take Photo")
                }
                Button(onClick = { galleryLauncher.launch("image/*") }) {
                    Text("Gallery")
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            PhotoGallery(photos = issue!!.photos)
            
            Spacer(modifier = Modifier.height(16.dp))
            
            CommentThread(comments = issue!!.comments)
            
            CommentInputField { text ->
                viewModel.addComment(text)
            }
        }
    }
}
""")
