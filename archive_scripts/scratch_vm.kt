
    fun stopRecording() {
        viewModelScope.launch {
            _isRecording.value = false
            timerJob?.cancel()
            waypointJob?.cancel()

            currentPathId?.let { pathId ->
                _isSaving.value = true
                pathRepository.stopRecordingPath(pathId)
                
                // Observe WorkManager for completion
                val workManager = androidx.work.WorkManager.getInstance(getApplication())
                val liveData = workManager.getWorkInfosForUniqueWorkLiveData("space360_sync_queue_immediate")
                
                val observer = object : androidx.lifecycle.Observer<List<androidx.work.WorkInfo>> {
                    override fun onChanged(workInfos: List<androidx.work.WorkInfo>?) {
                        if (workInfos.isNullOrEmpty()) return
                        val info = workInfos.first()
                        if (info.state.isFinished) {
                            _isSaving.value = false
                            liveData.removeObserver(this)
                        }
                    }
                }
                kotlinx.coroutines.Dispatchers.Main.invoke {
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

