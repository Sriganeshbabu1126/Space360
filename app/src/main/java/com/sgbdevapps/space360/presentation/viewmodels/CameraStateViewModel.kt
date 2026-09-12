package com.sgbdevapps.space360.presentation.viewmodels

import android.bluetooth.BluetoothDevice
import android.util.Log
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.service.CameraRecordingState
import com.sgbdevapps.space360.service.ConnectionProgress
import com.sgbdevapps.space360.service.Insta360SyncManager
import com.sgbdevapps.space360.service.PathRecordingState
import com.sgbdevapps.space360.service.SyncStatus
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class CameraStateViewModel @Inject constructor(
    private val insta360SyncManager: Insta360SyncManager,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val TAG = "SPACE360_INSTA360"

    val pathRecordingState: StateFlow<PathRecordingState> = insta360SyncManager.pathRecordingState
    val cameraRecordingState: StateFlow<CameraRecordingState> = insta360SyncManager.cameraRecordingState
    val syncStatus: StateFlow<SyncStatus> = insta360SyncManager.syncStatus
    val errorMessage: StateFlow<String?> = insta360SyncManager.errorMessage
    val recordingSession = insta360SyncManager.recordingSession
    val syncTimingStatus = insta360SyncManager.syncTimingStatus

    private val _connectionProgress = MutableStateFlow<ConnectionProgress?>(null)
    val connectionProgress: StateFlow<ConnectionProgress?> = _connectionProgress.asStateFlow()

    fun startRecording() {
        viewModelScope.launch {
            val result = insta360SyncManager.startPathAndCameraRecording("SGB Test Construction Site")
            if (result.isSuccess) {
                Log.d(TAG, "Recording started")
            } else {
                Log.e(TAG, "Failed to start path recording")
            }
        }
    }

    fun startCameraRecording() {
        viewModelScope.launch {
            // Wait for path ID if needed, here we just start camera
            insta360SyncManager.startCameraRecordingForPath("current-path")
        }
    }

    fun stopRecording() {
        viewModelScope.launch {
            insta360SyncManager.stopPathAndCameraRecording()
            Log.d(TAG, "Recording stopped")
        }
    }

    fun connectCamera(device: BluetoothDevice) {
        viewModelScope.launch {
            insta360SyncManager.connectToCamera(device).collect { progress ->
                _connectionProgress.value = progress
                if (progress.progress == 1.0f) {
                    _connectionProgress.value = null // clear on success
                }
            }
        }
    }

    fun reconnectCamera() {
        // Find last device or launch scanner logic, placeholder for simplicity
        clearError()
        Log.d(TAG, "Reconnect requested")
    }

    fun clearError() {
        insta360SyncManager.clearError()
    }
}
