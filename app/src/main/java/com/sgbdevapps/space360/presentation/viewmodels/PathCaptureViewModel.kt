package com.sgbdevapps.space360.presentation.viewmodels

import android.app.Application
import android.content.Intent
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.domain.repository.AuthRepository
import com.sgbdevapps.space360.domain.repository.PathRepository
import com.sgbdevapps.space360.service.GpsTrackingService
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class PathCaptureViewModel @Inject constructor(
    application: Application,
    private val pathRepository: PathRepository,
    private val authRepository: AuthRepository
) : AndroidViewModel(application) {

    private val _isRecording = MutableStateFlow(false)
    val isRecording: StateFlow<Boolean> = _isRecording

    private val _waypointCount = MutableStateFlow(0)
    val waypointCount: StateFlow<Int> = _waypointCount

    private val _elapsedTimeSeconds = MutableStateFlow(0)
    val elapsedTimeSeconds: StateFlow<Int> = _elapsedTimeSeconds

    private var currentPathId: String? = null
    private var timerJob: Job? = null
    private var waypointJob: Job? = null

    fun startRecording(siteId: String) {
        viewModelScope.launch {
            val userResult = authRepository.getCurrentUser()
            val userId = userResult.getOrNull()?.id ?: "unknown"
            val pathId = pathRepository.startRecordingPath(siteId, userId)
            currentPathId = pathId

            _isRecording.value = true
            _elapsedTimeSeconds.value = 0
            
            // Start Timer
            timerJob?.cancel()
            timerJob = viewModelScope.launch {
                while (_isRecording.value) {
                    delay(1000)
                    _elapsedTimeSeconds.value += 1
                }
            }

            // Observe waypoints
            waypointJob?.cancel()
            waypointJob = viewModelScope.launch {
                pathRepository.observeWaypointCount(pathId).collectLatest {
                    _waypointCount.value = it
                }
            }

            // Start Foreground Service
            val intent = Intent(getApplication(), GpsTrackingService::class.java).apply {
                action = GpsTrackingService.ACTION_START
                putExtra(GpsTrackingService.EXTRA_PATH_ID, pathId)
            }
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                getApplication<Application>().startForegroundService(intent)
            } else {
                getApplication<Application>().startService(intent)
            }
        }
    }

    private val _isSaving = MutableStateFlow(false)
    val isSaving: StateFlow<Boolean> = _isSaving

    fun stopRecording() {
        viewModelScope.launch {
            _isRecording.value = false
            timerJob?.cancel()
            waypointJob?.cancel()

            currentPathId?.let { pathId ->
                _isSaving.value = true
                pathRepository.stopRecordingPath(pathId)
                
                kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                    val workManager = androidx.work.WorkManager.getInstance(getApplication())
                    val liveData = workManager.getWorkInfosForUniqueWorkLiveData("space360_sync_queue_immediate")
                    
                    val observer = object : androidx.lifecycle.Observer<List<androidx.work.WorkInfo>> {
                        override fun onChanged(workInfos: List<androidx.work.WorkInfo>) {
                            if (workInfos.isNullOrEmpty()) return
                            val info = workInfos.first()
                            if (info.state.isFinished) {
                                _isSaving.value = false
                                liveData.removeObserver(this)
                            }
                        }
                    }
                    liveData.observeForever(observer)
                }
            }
            
            val intent = Intent(getApplication(), GpsTrackingService::class.java).apply {
                action = GpsTrackingService.ACTION_STOP
            }
            getApplication<Application>().startService(intent)
            
            currentPathId = null
        }
    }
    
    fun discardRecording() {
        viewModelScope.launch {
            _isRecording.value = false
            timerJob?.cancel()
            waypointJob?.cancel()

            currentPathId?.let { pathId ->
                pathRepository.discardPath(pathId)
            }
            
            val intent = Intent(getApplication(), GpsTrackingService::class.java).apply {
                action = GpsTrackingService.ACTION_STOP
            }
            getApplication<Application>().startService(intent)
            
            currentPathId = null
            _waypointCount.value = 0
            _elapsedTimeSeconds.value = 0
        }
    }
}
