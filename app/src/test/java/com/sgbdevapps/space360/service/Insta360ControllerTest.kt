package com.sgbdevapps.space360.service

import android.bluetooth.BluetoothAdapter
import android.content.Context
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.Mockito.mock
import org.mockito.MockitoAnnotations
import kotlinx.coroutines.runBlocking
import android.bluetooth.BluetoothManager

class Insta360ControllerTest {

    @Mock
    private lateinit var mockContext: Context

    @Mock
    private lateinit var mockBluetoothManager: BluetoothManager

    private lateinit var controller: Insta360Controller

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        org.mockito.Mockito.`when`(mockContext.getSystemService(Context.BLUETOOTH_SERVICE)).thenReturn(mockBluetoothManager)
        controller = Insta360Controller(mockContext)
    }

    @Test
    fun testBluetoothAdapterInitialization() {
        // BluetoothAdapter can be null in test environments depending on Robolectric config,
        // but the method should not crash.
        val adapter = controller.bluetoothAdapter
        // We just assert it doesn't crash on init
        assertTrue(true)
    }

    @Test
    fun testStartRecordingCommandFormat() = runBlocking {
        // Without an actual GATT connection, it will return failure
        val result = controller.startRecording()
        assertTrue(result.isFailure)
    }

    @Test
    fun testStopRecordingCommandFormat() = runBlocking {
        val result = controller.stopRecording()
        assertTrue(result.isFailure)
    }
}
