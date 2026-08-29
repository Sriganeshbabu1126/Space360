package com.sgbdevapps.space360.presentation.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatusUpdateBottomSheet(
    currentStatus: String,
    onUpdateStatus: (String) -> Unit,
    onDismiss: () -> Unit
) {
    val validTransitions = when (currentStatus) {
        "Open" -> listOf("In Progress")
        "In Progress" -> listOf("Done")
        else -> emptyList() // Done -> no transitions
    }

    if (validTransitions.isEmpty()) {
        AlertDialog(
            onDismissRequest = onDismiss,
            title = { Text("Status Update") },
            text = { Text("This issue cannot be transitioned further from status: $currentStatus") },
            confirmButton = {
                TextButton(onClick = onDismiss) { Text("OK") }
            }
        )
        return
    }

    var selectedStatus by remember { mutableStateOf(validTransitions.first()) }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Change Issue Status",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            Text(
                text = "Current status: $currentStatus",
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            Column(Modifier.selectableGroup()) {
                validTransitions.forEach { status ->
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .height(56.dp)
                            .selectable(
                                selected = (status == selectedStatus),
                                onClick = { selectedStatus = status },
                                role = Role.RadioButton
                            )
                            .padding(horizontal = 16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = (status == selectedStatus),
                            onClick = null // null recommended for accessibility with selectable
                        )
                        Text(
                            text = status,
                            style = MaterialTheme.typography.bodyLarge,
                            modifier = Modifier.padding(start = 16.dp)
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.End
            ) {
                TextButton(onClick = onDismiss) {
                    Text("Cancel")
                }
                Spacer(modifier = Modifier.width(8.dp))
                Button(onClick = { 
                    onUpdateStatus(selectedStatus)
                    onDismiss()
                }) {
                    Text("Update")
                }
            }
            Spacer(modifier = Modifier.height(32.dp)) // Padding for nav bar
        }
    }
}
