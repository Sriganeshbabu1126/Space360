package com.sgbdevapps.space360.presentation.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sgbdevapps.space360.domain.model.Issue

@Composable
fun IssueCard(
    issue: Issue,
    onRetrySync: () -> Unit = {},
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .clickable { onClick() }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = issue.title, fontWeight = FontWeight.Bold, fontSize = 16.sp, modifier = Modifier.weight(1f))
                if (issue.syncStatus != null) {
                    IssueSyncStatusBadge(
                        syncStatus = issue.syncStatus,
                        onRetry = onRetrySync
                    )
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
            Row(modifier = Modifier.fillMaxWidth()) {
                StatusBadge(issue.status)
                Spacer(modifier = Modifier.width(8.dp))
                Text(text = "Priority: ${issue.priority}", fontSize = 12.sp)
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(text = "Assigned: ${issue.assignedToName}", fontSize = 12.sp)
        }
    }
}
