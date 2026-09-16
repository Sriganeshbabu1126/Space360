package com.sgbdevapps.space360.presentation.viewmodels

import android.app.Application
import android.content.Intent
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.domain.repository.AuthRepository
import com.sgbdevapps.space360.domain.SessionManager
import com.sgbdevapps.space360.domain.repository.PathRepository
import com.sgbdevapps.space360.service.GpsTrackingService
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.filterNotNull
import kotlinx.coroutines.flow.distinctUntilChanged
import timber.log.Timber
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class PathCaptureViewModel @Inject constructor(
    application: Application,
    private val pathRepository: PathRepository,
    private val authRepository: AuthRepository,
    private val sessionManager: SessionManager
) : AndroidViewModel(application) {

    init {
        // Observe activeProjectId as Flow — reacts when project becomes available
        viewModelScope.launch {
            sessionManager.selectedSite
                .filterNotNull()
                .distinctUntilChanged()
                .collect { site ->
                    loadFloorPlan(site.id)
                }
        }

        // Safety net — never spin forever
        viewModelScope.launch {
            delay(6_000L)
            if (_floorPlanLoadState.value is com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loading) {
                Timber.w("Floor plan timeout — showing placeholder")
                _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.NoFloorPlan
            }
        }
    }

    val selectedSite = sessionManager.selectedSite

    private val _isLocationPinned = MutableStateFlow(false)
    val isLocationPinned: StateFlow<Boolean> = _isLocationPinned
    
    fun pinLocation() {
        _isLocationPinned.value = true
        // CrashlyticsHelper.logEvent("Location pinned for recording")
    }
    private val _showLocationPicker = MutableStateFlow(false)
    val showLocationPicker: StateFlow<Boolean> = _showLocationPicker
    
    private val _pinnedLocation = MutableStateFlow<Pair<Double, Double>?>(null)
    val pinnedLocation: StateFlow<Pair<Double, Double>?> = _pinnedLocation
    
    private val _floorPlanLoadState = MutableStateFlow<com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState>(com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loading)
    val floorPlanLoadState: StateFlow<com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState> = _floorPlanLoadState
    
    fun openLocationPicker() {
        _showLocationPicker.value = true
    }
    
    fun closeLocationPicker() {
        _showLocationPicker.value = false
    }
    
    fun pinLocationInteractive(lat: Double, lng: Double) {
        _pinnedLocation.value = Pair(lat, lng)
        _isLocationPinned.value = true
        _showLocationPicker.value = false
    }

    
    fun unpinLocation() {
        _isLocationPinned.value = false
        if (_isRecording.value) {
            stopRecording()
        }
    }

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

            android.util.Log.e("SPACE360_DEBUG", "Recording started at ${System.currentTimeMillis()}")

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
    private val _saveStatus = MutableStateFlow<String?>(null)
    val saveStatus: StateFlow<String?> = _saveStatus

    
    fun pauseRecording() {
        _isRecording.value = false
        timerJob?.cancel()
        waypointJob?.cancel()
        // Stop the GPS tracking service intent in a real scenario
    }

    fun stopRecording() {
        viewModelScope.launch {
            _isRecording.value = false
            timerJob?.cancel()
            waypointJob?.cancel()

            android.util.Log.e("SPACE360_DEBUG", "Recording stopped. Total waypoints: ${_waypointCount.value}")

            currentPathId?.let { pathId ->
                _isSaving.value = true
                _saveStatus.value = "Saving Path..."
                android.util.Log.e("SPACE360_DEBUG", "Saving path to Room database...")
                try {
                    pathRepository.stopRecordingPath(pathId)
                    android.util.Log.e("SPACE360_DEBUG", "Path saved with ID: $pathId")
                    _saveStatus.value = "Path Saved Successfully"
                } catch(e: Exception) {
                    _saveStatus.value = "Failed to Save Path: ${e.message}"
                }
                
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
                                // Clear status after a short delay so user can read it
                                viewModelScope.launch {
                                    delay(2000)
                                    _saveStatus.value = null
                                }
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
    private suspend fun loadFloorPlan(projectId: String) {
        try {
            _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loading
            
            // Re-fetch site just in case, but we already have it from sessionManager
            val site = sessionManager.selectedSite.value
            val url = site?.floorPlanUrl
            
            _floorPlanLoadState.value = if (!url.isNullOrBlank()) {
                com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.Loaded(url)
            } else {
                com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.NoFloorPlan
            }
        } catch (e: Exception) {
            Timber.e(e, "loadFloorPlan failed")
            _floorPlanLoadState.value = com.sgbdevapps.space360.presentation.screens.FloorPlanLoadState.NoFloorPlan
        }
    }
}
