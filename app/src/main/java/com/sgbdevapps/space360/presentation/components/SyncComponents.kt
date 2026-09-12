package com.sgbdevapps.space360.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun OfflineBanner(
    isOnline: Boolean,
    pendingSyncCount: Int
) {
    if (!isOnline) {
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color(0xFFFF9800)),
            color = Color(0xFFFF9800)
        ) {
            Row(
                modifier = Modifier
                    .padding(horizontal = 16.dp, vertical = 8.dp)
                    .height(40.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    modifier = Modifier.weight(1f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(16.dp),
                        strokeWidth = 2.dp,
                        color = Color.White
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = if (pendingSyncCount > 0) {
                            "Offline — $pendingSyncCount pending"
                        } else {
                            "Offline"
                        },
                        color = Color.White,
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
        }
    }
}

@Composable
fun IssueSyncStatusBadge(
    syncStatus: String?,
    onRetry: () -> Unit = {}
) {
    when (syncStatus) {
        "PENDING", "SYNCING" -> {
            Surface(
                shape = RoundedCornerShape(4.dp),
                color = Color(0xFFFFF3E0) // Light amber
            ) {
                Row(
                    modifier = Modifier.padding(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(12.dp),
                        strokeWidth = 1.dp,
                        color = Color(0xFFFF9800)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        "Syncing",
                        fontSize = 10.sp,
                        color = Color(0xFFFF9800)
                    )
                }
            }
        }
        "FAILED" -> {
            Surface(
                shape = RoundedCornerShape(4.dp),
                color = Color(0xFFFFEBEE) // Light red
            ) {
                Row(
                    modifier = Modifier.padding(6.dp).clickable { onRetry() },
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text(
                        "Retry",
                        fontSize = 10.sp,
                        color = Color(0xFFF44336)
                    )
                }
            }
        }
        "SYNCED" -> {
            // No badge needed
        }
    }
}
