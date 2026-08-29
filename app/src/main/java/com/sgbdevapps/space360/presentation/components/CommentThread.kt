package com.sgbdevapps.space360.presentation.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sgbdevapps.space360.domain.model.IssueComment

@Composable
fun CommentThread(comments: List<IssueComment>) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
    ) {
        Text(
            text = "Comments",
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        if (comments.isEmpty()) {
            Text("No comments yet", color = MaterialTheme.colorScheme.onSurfaceVariant)
        } else {
            comments.forEach { comment ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = comment.userName,
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp
                            )
                            // Display pending badge if status is PENDING
                            // Assuming syncStatus is added or we pass it
                            // For now, check if id is negative (temporary)
                            if (comment.id < 0) {
                                Badge { Text("Pending") }
                            }
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(text = comment.text, fontSize = 14.sp)
                    }
                }
            }
        }
    }
}
