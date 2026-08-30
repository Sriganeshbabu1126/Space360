package com.sgbdevapps.space360.presentation.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun CommentInputField(
    isOnline: Boolean,
    onSendComment: (String) -> Unit
) {
    var text by remember { mutableStateOf("") }
    
    Column(modifier = Modifier.fillMaxWidth().padding(8.dp)) {
        if (!isOnline) {
            Text(
                text = "Offline — comment queued when online",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(bottom = 4.dp)
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = text,
                onValueChange = { if (it.length <= 500) text = it },
                modifier = Modifier.weight(1f),
                placeholder = { Text("Add a comment...") },
                maxLines = 4
            )
            IconButton(
                onClick = { 
                    onSendComment(text)
                    text = "" 
                },
                enabled = text.isNotBlank()
            ) {
                Icon(Icons.Default.Send, contentDescription = "Send Comment")
            }
        }
    }
}
