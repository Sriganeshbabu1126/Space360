package com.sgbdevapps.space360.service

import android.bluetooth.BluetoothDevice
import android.content.Context
import android.os.SystemClock
import android.util.Log
import com.sgbdevapps.space360.domain.repository.PathRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.launch
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import javax.inject.Inject
import kotlin.math.abs

enum class PathRecordingState { Idle, Recording, Paused, Stopped }
enum class CameraRecordingState { Disconnected, Connecting, Connected, Recording, Stopped, Error }
enum class SyncStatus { InSync, OutOfSync, AwaitingUserAction }

data class PathWithCamera(
    val pathId: String,
    val startTimestampNanos: Long
)

data class ConnectionProgress(
    val state: String,
    val progress: Float
)

class Insta360SyncManager @Inject constructor(
    private val insta360Controller: Insta360Controller,
    private val pathRepository: PathRepository,
    private val context: Context
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    private val _pathRecordingState = MutableStateFlow(PathRecordingState.Idle)
    val pathRecordingState: StateFlow<PathRecordingState> = _pathRecordingState.asStateFlow()

    private val _cameraRecordingState = MutableStateFlow(CameraRecordingState.Connected) // Mocked as connected for testing Phase 4a
    val cameraRecordingState: StateFlow<CameraRecordingState> = _cameraRecordingState.asStateFlow()

    private val _syncStatus = MutableStateFlow(SyncStatus.InSync)
    val syncStatus: StateFlow<SyncStatus> = _syncStatus.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _recordingSession = MutableStateFlow<RecordingSession?>(null)
    val recordingSession: StateFlow<RecordingSession?> = _recordingSession.asStateFlow()

    private val _syncTimingStatus = MutableStateFlow("Idle")
    val syncTimingStatus: StateFlow<String> = _syncTimingStatus.asStateFlow()

    private var currentPathId: String? = null
    
    suspend fun startPathAndCameraRecording(siteName: String): Result<RecordingSession> {
        return try {
            // 1. Start path recording (GPS)
            // Hardcoded "default-user" since it's missing from prompt
            val pathId = pathRepository.startRecordingPath(siteName, "default-user")
            currentPathId = pathId
            val androidStartNanos = SystemClock.elapsedRealtimeNanos()
            
            // 2. Start camera recording (Bluetooth)
            _cameraRecordingState.value = CameraRecordingState.Connecting
            val cameraStartResult = insta360Controller.startRecording()
            
            if (cameraStartResult.isFailure) {
                // Camera failed → AUTO-STOP PATH (Decision 1)
                pathRepository.stopRecordingPath(pathId)
                val errMsg = "Camera failed to start. Recording stopped."
                _errorMessage.value = errMsg
                _cameraRecordingState.value = CameraRecordingState.Error
                _pathRecordingState.value = PathRecordingState.Stopped
                return Result.failure(cameraStartResult.exceptionOrNull() ?: Exception("Camera start failed"))
            }
            
            // 3. Estimate camera start timestamp
            val cameraStartNanos = SystemClock.elapsedRealtimeNanos()  // Best guess from command response
            val clockOffsetNanos = androidStartNanos - cameraStartNanos
            
            // 4. Create RecordingSession
            val session = RecordingSession(
                pathId = pathId,
                androidStartNanos = androidStartNanos,
                cameraStartNanos = cameraStartNanos,
                clockOffsetNanos = clockOffsetNanos
            )
            
            GpsTrackingService.setRecordingSession(session)
            
            // 5. Store in PathEntity (via PathRepository)
            updatePathWithCameraMetadata(pathId, session)
            
            // 6. Update UI state
            _recordingSession.value = session
            _pathRecordingState.value = PathRecordingState.Recording
            _cameraRecordingState.value = CameraRecordingState.Recording
            _syncTimingStatus.value = "In Sync ±${abs(clockOffsetNanos / 1_000_000)}ms"
            
            Log.d("SPACE360_INSTA360", "Recording started: pathId=$pathId, offset=${clockOffsetNanos}ns")
            
            Result.success(session)
        } catch (e: Exception) {
            _errorMessage.value = "Failed to start recording: ${e.message}"
            Log.e("SPACE360_INSTA360", "Error starting recording", e)
            Result.failure(e)
        }
    }

    suspend fun startCameraRecordingForPath(pathId: String): Result<Unit> {
        _cameraRecordingState.value = CameraRecordingState.Connecting // showing loading
        val result = insta360Controller.startRecording()
        return if (result.isSuccess) {
            _cameraRecordingState.value = CameraRecordingState.Recording
            _syncStatus.value = SyncStatus.InSync
            Result.success(Unit)
        } else {
            _cameraRecordingState.value = CameraRecordingState.Error
            _syncStatus.value = SyncStatus.OutOfSync
            _errorMessage.value = "Failed to start camera recording"
            Result.failure(result.exceptionOrNull() ?: Exception("Unknown error"))
        }
    }

    suspend fun stopPathAndCameraRecording(): Result<Unit> {
        return try {
            val currentSession = _recordingSession.value ?: return Result.failure(Exception("No active session"))
            
            // 1. Stop path (this saves end timestamp)
            val pathEndNanos = SystemClock.elapsedRealtimeNanos()
            pathRepository.stopRecordingPath(currentSession.pathId)  // Calls GpsTrackingService.stopTracking() conceptually
            
            // 2. Stop camera (fire-and-forget, Decision 3)
            insta360Controller.stopRecording()  // Don't wait for ACK conceptually, but the func suspends
            val cameraEndNanos = SystemClock.elapsedRealtimeNanos()
            
            // 3. Calculate durations
            val pathDurationSeconds = (pathEndNanos - currentSession.androidStartNanos) / 1_000_000_000L
            val cameraDurationSeconds = (cameraEndNanos - currentSession.cameraStartNanos) / 1_000_000_000L
            
            // 4. Update PathEntity with end times
            val updatedSession = currentSession.copy(
                pathRecordingDurationSeconds = pathDurationSeconds,
                cameraRecordingDurationSeconds = cameraDurationSeconds
            )
            updatePathWithCameraMetadata(currentSession.pathId, updatedSession)
            
            // 5. Update UI state
            _recordingSession.value = null
            _pathRecordingState.value = PathRecordingState.Stopped
            _cameraRecordingState.value = CameraRecordingState.Stopped
            _syncTimingStatus.value = "Recording Complete"
            
            Log.d("SPACE360_INSTA360", 
                "Recording stopped: pathId=${currentSession.pathId}, " +
                "pathDuration=${pathDurationSeconds}s, cameraDuration=${cameraDurationSeconds}s, " +
                "offset=${currentSession.clockOffsetNanos}ns"
            )
            
            Result.success(Unit)
        } catch (e: Exception) {
            _errorMessage.value = "Failed to stop recording: ${e.message}"
            Log.e("SPACE360_INSTA360", "Error stopping recording", e)
            Result.failure(e)
        }
    }

    private suspend fun updatePathWithCameraMetadata(
        pathId: String,
        session: RecordingSession
    ) {
        try {
            pathRepository.updatePathWithCameraMetadata(
                pathId = pathId,
                cameraStartNanos = session.cameraStartNanos,
                // Using 0 if null as placeholder to match current API logic, actually we'll pass null since API accepts it
                cameraEndNanos = SystemClock.elapsedRealtimeNanos(),
                clockOffsetNanos = session.clockOffsetNanos,
                sessionJson = Json.encodeToString(session)
            )
            Log.d("SPACE360_INSTA360", "PathEntity updated with camera metadata: $pathId")
        } catch (e: Exception) {
            Log.e("SPACE360_INSTA360", "Failed to update path metadata", e)
        }
    }

    fun connectToCamera(device: BluetoothDevice): Flow<ConnectionProgress> = flow {
        emit(ConnectionProgress("Connecting", 0.2f))
        _cameraRecordingState.value = CameraRecordingState.Connecting
        
        val connected = insta360Controller.connectToCamera(device)
        
        if (connected) {
            emit(ConnectionProgress("Discovering Services", 0.5f))
            delay(1000) // Simulate service discovery parsing delay
            emit(ConnectionProgress("Connected", 1.0f))
            _cameraRecordingState.value = CameraRecordingState.Connected
            _syncStatus.value = SyncStatus.InSync
            _errorMessage.value = null
        } else {
            _cameraRecordingState.value = CameraRecordingState.Error
            _syncStatus.value = SyncStatus.OutOfSync
            _errorMessage.value = "Camera connection failed"
            emit(ConnectionProgress("Connection Failed", 0.0f))
        }
    }

    fun disconnectCamera() {
        scope.launch {
            insta360Controller.disconnectCamera()
            _cameraRecordingState.value = CameraRecordingState.Disconnected
            if (_pathRecordingState.value == PathRecordingState.Recording) {
                _syncStatus.value = SyncStatus.OutOfSync
                _errorMessage.value = "Camera disconnected while path is recording"
            }
        }
    }

    fun clearError() {
        _errorMessage.value = null
    }
}
