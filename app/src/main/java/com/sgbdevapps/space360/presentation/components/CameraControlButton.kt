package com.sgbdevapps.space360.presentation.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.sgbdevapps.space360.service.CameraRecordingState

@Composable
fun CameraConnectionStatus(
    state: CameraRecordingState,
    batteryLevel: Int?,
    onReconnect: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        val statusText = when (state) {
            CameraRecordingState.Disconnected -> "Disconnected"
            CameraRecordingState.Connecting -> "Connecting..."
            CameraRecordingState.Connected -> "Connected"
            CameraRecordingState.Recording -> "Recording"
            CameraRecordingState.Stopped -> "Stopped"
            CameraRecordingState.Error -> "Connection Error"
        }
        
        SuggestionChip(
            onClick = { if (state == CameraRecordingState.Error) onReconnect() },
            label = { Text("Status: $statusText") }
        )
        
        if (state == CameraRecordingState.Connected || state == CameraRecordingState.Recording) {
            Spacer(modifier = Modifier.width(8.dp))
            SuggestionChip(
                onClick = { },
                label = { Text("Battery: ${batteryLevel ?: 100}%") }
            )
        }
    }
}

@Composable
fun CameraControlButton(
    state: CameraRecordingState,
    onStartClick: () -> Unit,
    onStopClick: () -> Unit,
    isPathRecording: Boolean,
    onConnectClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val buttonConfig = when (state) {
        CameraRecordingState.Disconnected, CameraRecordingState.Error -> {
            Triple(
                "🔴 Connect Camera", 
                MaterialTheme.colorScheme.primary, 
                isPathRecording
            ) to onConnectClick
        }
        CameraRecordingState.Connecting -> {
            Triple(
                "⏳ Connecting...", 
                MaterialTheme.colorScheme.secondary, 
                false
            ) to {}
        }
        CameraRecordingState.Connected -> {
            Triple(
                "🟢 Start Video", 
                Color(0xFF4CAF50), // Green
                true
            ) to onStartClick
        }
        CameraRecordingState.Recording -> {
            Triple(
                "⏹️ Stop Video", 
                MaterialTheme.colorScheme.error, 
                true
            ) to onStopClick
        }
        CameraRecordingState.Stopped -> {
            Triple(
                "✅ Recording Complete", 
                MaterialTheme.colorScheme.secondary, 
                false
            ) to {}
        }
    }

    val text = buttonConfig.first.first
    val color = buttonConfig.first.second
    val isEnabled = buttonConfig.first.third
    val onClickAction = buttonConfig.second

    Button(
        onClick = onClickAction,
        enabled = isEnabled,
        colors = ButtonDefaults.buttonColors(containerColor = color),
        modifier = modifier.fillMaxWidth().height(56.dp)
    ) {
        Text(text)
    }
    
    if (!isPathRecording && (state == CameraRecordingState.Disconnected || state == CameraRecordingState.Error)) {
        Text(
            "Start path recording first",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 4.dp)
        )
    }
}
