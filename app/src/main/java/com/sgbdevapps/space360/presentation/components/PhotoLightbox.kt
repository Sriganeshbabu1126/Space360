package com.sgbdevapps.space360.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.sgbdevapps.space360.domain.model.IssuePhoto

@Composable
fun PhotoLightbox(
    photos: List<IssuePhoto>,
    initialIndex: Int,
    onDismiss: () -> Unit
) {
    if (photos.isEmpty() || initialIndex !in photos.indices) return

    var currentIndex by remember { mutableStateOf(initialIndex) }
    val context = LocalContext.current

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black)
        ) {
            // Very simple full-screen image without swipe for now (to keep it simple)
            // A real app would use a Pager from Accompanist or Foundation
            AsyncImage(
                model = ImageRequest.Builder(context)
                    .data(photos[currentIndex].photoUrl)
                    .crossfade(true)
                    .build(),
                contentDescription = "Full Size Photo",
                contentScale = ContentScale.Fit,
                modifier = Modifier.fillMaxSize()
            )

            // Top bar
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "${currentIndex + 1} of ${photos.size}",
                    color = Color.White
                )
                IconButton(onClick = onDismiss) {
                    Icon(Icons.Default.Close, contentDescription = "Close", tint = Color.White)
                }
            }
            
            // Nav buttons (since we don't have Pager)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .align(Alignment.Center)
                    .padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Button(
                    onClick = { if (currentIndex > 0) currentIndex-- },
                    enabled = currentIndex > 0
                ) {
                    Text("<")
                }
                Button(
                    onClick = { if (currentIndex < photos.size - 1) currentIndex++ },
                    enabled = currentIndex < photos.size - 1
                ) {
                    Text(">")
                }
            }
        }
    }
}
