package com.sgbdevapps.space360.service

import android.os.SystemClock
import com.sgbdevapps.space360.domain.repository.PathRepository
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.mockito.ArgumentMatchers.anyString
import org.mockito.Mock
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.any
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.verify
import kotlinx.serialization.json.Json
import kotlinx.serialization.encodeToString

class Insta360SyncManagerTest {

    @Mock
    private lateinit var mockController: Insta360Controller
    
    @Mock
    private lateinit var mockRepository: PathRepository
    
    @Mock
    private lateinit var mockContext: android.content.Context
    
    private lateinit var syncManager: Insta360SyncManager

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        syncManager = Insta360SyncManager(mockController, mockRepository, mockContext)
    }

    @Test
    fun testStartRecordingCreatesRecordingSession() = runBlocking {
        `when`(mockRepository.startRecordingPath(anyString(), anyString())).thenReturn("path-123")
        `when`(mockController.startRecording()).thenReturn(Result.success(Unit))
        
        val result = syncManager.startPathAndCameraRecording("Site A")
        assertTrue(result.isSuccess)
        
        val session = result.getOrNull()
        assertNotNull(session)
        assertEquals("path-123", session?.pathId)
        assertTrue(session!!.androidStartNanos > 0)
        assertTrue(session.cameraStartNanos > 0)
        
        assertEquals(PathRecordingState.Recording, syncManager.pathRecordingState.first())
        assertEquals(CameraRecordingState.Recording, syncManager.cameraRecordingState.first())
    }

    @Test
    fun testClockOffsetCalculation() = runBlocking {
        `when`(mockRepository.startRecordingPath(anyString(), anyString())).thenReturn("path-123")
        `when`(mockController.startRecording()).thenReturn(Result.success(Unit))
        
        val result = syncManager.startPathAndCameraRecording("Site A")
        val session = result.getOrNull()!!
        
        val expectedOffset = session.androidStartNanos - session.cameraStartNanos
        assertEquals(expectedOffset, session.clockOffsetNanos)
    }

    @Test
    fun testCameraFailureAutoStopsPath() = runBlocking {
        `when`(mockRepository.startRecordingPath(anyString(), anyString())).thenReturn("path-123")
        `when`(mockController.startRecording()).thenReturn(Result.failure<Unit>(Exception("BLE failed")))
        
        val result = syncManager.startPathAndCameraRecording("Site A")
        assertTrue(result.isFailure)
        
        verify(mockRepository).stopRecordingPath("path-123")
        
        assertEquals(PathRecordingState.Stopped, syncManager.pathRecordingState.first())
        assertEquals(CameraRecordingState.Error, syncManager.cameraRecordingState.first())
        assertTrue(syncManager.errorMessage.first()?.contains("failed") == true)
    }

    @Test
    fun testStopRecordingStoresDurations() = runBlocking {
        `when`(mockRepository.startRecordingPath(anyString(), anyString())).thenReturn("path-123")
        `when`(mockController.startRecording()).thenReturn(Result.success(Unit))
        `when`(mockController.stopRecording()).thenReturn(Result.success(Unit))
        
        syncManager.startPathAndCameraRecording("Site A")
        
        val stopResult = syncManager.stopPathAndCameraRecording()
        assertTrue(stopResult.isSuccess)
        
        assertEquals(PathRecordingState.Stopped, syncManager.pathRecordingState.first())
        assertEquals(CameraRecordingState.Stopped, syncManager.cameraRecordingState.first())
    }

    @Test
    fun testPathEntityUpdateWithCameraMetadata() = runBlocking {
        `when`(mockRepository.startRecordingPath(anyString(), anyString())).thenReturn("path-123")
        `when`(mockController.startRecording()).thenReturn(Result.success(Unit))
        
        syncManager.startPathAndCameraRecording("Site A")
        
        verify(mockRepository).updatePathWithCameraMetadata(
            pathId = anyString(),
            cameraStartNanos = any(),
            cameraEndNanos = anyOrNull(),
            clockOffsetNanos = any(),
            sessionJson = anyString()
        )
    }

    @Test
    fun testRecordingSessionJsonSerialization() {
        val session = RecordingSession(
            pathId = "p-123",
            androidStartNanos = 1000L,
            cameraStartNanos = 900L,
            clockOffsetNanos = 100L
        )
        
        val jsonStr = Json.encodeToString(session)
        assertTrue(jsonStr.contains("p-123"))
        assertTrue(jsonStr.contains("1000"))
        
        val decoded = Json.decodeFromString<RecordingSession>(jsonStr)
        assertEquals(session.pathId, decoded.pathId)
        assertEquals(session.clockOffsetNanos, decoded.clockOffsetNanos)
    }
}
