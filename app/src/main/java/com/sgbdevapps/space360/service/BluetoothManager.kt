package com.sgbdevapps.space360.service

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.delay

data class BluetoothDevice(val name: String?, val address: String)

@Singleton
class BluetoothManager @Inject constructor() {
    private val _discoveredDevices = MutableStateFlow<List<BluetoothDevice>>(emptyList())
    val discoveredDevices: StateFlow<List<BluetoothDevice>> = _discoveredDevices.asStateFlow()

    suspend fun startDiscovery() {
        // Mock discovery
        _discoveredDevices.value = emptyList()
        delay(1000)
        _discoveredDevices.value = listOf(
            BluetoothDevice("Insta360 X4 (Fake)", "00:11:22:33:44:55"),
            BluetoothDevice("Unknown Device", "11:22:33:44:55:66")
        )
    }

    suspend fun connectToDevice(device: BluetoothDevice) {
        // Mock connect
        delay(1000)
    }

    fun disconnect() {
        // Mock disconnect
    }
}
