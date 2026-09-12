package com.sgbdevapps.space360.service

import kotlinx.serialization.Serializable

@Serializable
data class RecordingSession(
    val pathId: String,
    val androidStartNanos: Long,        // SystemClock.elapsedRealtimeNanos() when path starts
    val cameraStartNanos: Long,         // Estimated from Bluetooth START command response time
    val clockOffsetNanos: Long,         // androidStartNanos - cameraStartNanos
    val pathRecordingDurationSeconds: Long = 0,  // calculated at stop
    val cameraRecordingDurationSeconds: Long = 0  // estimated from camera response
)
