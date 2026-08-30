package com.sgbdevapps.space360.presentation.components

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.sgbdevapps.space360.domain.model.IssuePhoto

@Composable
fun PhotoGallery(
    photos: List<IssuePhoto>,
    isOnline: Boolean,
    onAddPhotos: (List<String>) -> Unit,
    onPhotoClick: (Int) -> Unit
) {
    val context = LocalContext.current
    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetMultipleContents()
    ) { uris: List<Uri> ->
        // Convert URIs to local file paths or handle them securely
        // In a real app we would copy them to cache dir first to get a file path
        // For demonstration, we pass string representations
        val paths = uris.map { it.toString() }
        if (paths.isNotEmpty()) {
            onAddPhotos(paths)
        }
    }

    Column(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Evidence Photos (${photos.size})",
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp
            )
            IconButton(
                onClick = { launcher.launch("image/*") },
                // Allow selecting photos even offline (they get queued)
            ) {
                Icon(Icons.Default.Add, contentDescription = "Add Photos")
            }
        }
        
        LazyVerticalGrid(
            columns = GridCells.Adaptive(100.dp),
            modifier = Modifier.heightIn(max = 300.dp),
            contentPadding = PaddingValues(4.dp)
        ) {
            itemsIndexed(photos) { index, photo ->
                Card(
                    modifier = Modifier
                        .padding(4.dp)
                        .size(100.dp)
                        .clickable { onPhotoClick(index) }
                ) {
                    Box {
                        AsyncImage(
                            model = ImageRequest.Builder(context)
                                .data(photo.photoUrl)
                                .crossfade(true)
                                .build(),
                            contentDescription = "Evidence Photo",
                            contentScale = ContentScale.Crop,
                            modifier = Modifier.fillMaxSize()
                        )
                        // If id is negative, it's pending
                        if (false) {
                            Badge(
                                modifier = Modifier.align(Alignment.TopEnd).padding(4.dp)
                            ) {
                                Text("Pending")
                            }
                        }
                    }
                }
            }
        }
    }
}
