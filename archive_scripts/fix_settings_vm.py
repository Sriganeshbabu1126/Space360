import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/SettingsViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

replacement = """package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.data.datastore.UserPreferences
import com.sgbdevapps.space360.data.model.ColorScheme
import com.sgbdevapps.space360.service.BluetoothDevice
import com.sgbdevapps.space360.service.BluetoothManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

sealed class BluetoothStatus {
    object DISCONNECTED : BluetoothStatus()
    object SEARCHING : BluetoothStatus()
    data class CONNECTED(val deviceName: String) : BluetoothStatus()
    object ERROR : BluetoothStatus()
}

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val userPreferences: UserPreferences,
    private val bluetoothManager: BluetoothManager
) : ViewModel() {

    private val _colorScheme = MutableStateFlow(ColorScheme.DEFAULT)
    val colorScheme = _colorScheme.asStateFlow()

    private val _bluetoothStatus = MutableStateFlow<BluetoothStatus>(BluetoothStatus.DISCONNECTED)
    val bluetoothStatus: StateFlow<BluetoothStatus> = _bluetoothStatus.asStateFlow()

    private val _availableDevices = MutableStateFlow<List<BluetoothDevice>>(emptyList())
    val availableDevices: StateFlow<List<BluetoothDevice>> = _availableDevices.asStateFlow()

    private val _isSearching = MutableStateFlow(false)
    val isSearching: StateFlow<Boolean> = _isSearching.asStateFlow()

    init {
        viewModelScope.launch {
            userPreferences.colorSchemeFlow.collect { schemeName ->
                val scheme = try {
                    ColorScheme.valueOf(schemeName)
                } catch (e: Exception) {
                    ColorScheme.DEFAULT
                }
                _colorScheme.value = scheme
            }
        }
    }

    fun setColorScheme(scheme: ColorScheme) {
        viewModelScope.launch {
            userPreferences.setColorScheme(scheme.name)
        }
    }

    fun initiateBluetooth() {
        viewModelScope.launch {
            try {
                _isSearching.value = true
                _bluetoothStatus.value = BluetoothStatus.SEARCHING
                
                // Start discovery
                bluetoothManager.startDiscovery()
                
                // Listen for discovered devices
                bluetoothManager.discoveredDevices.collect { devices ->
                    val insta360Devices = devices.filter { 
                        it.name?.contains("Insta360", ignoreCase = true) == true ||
                        it.name?.contains("X4", ignoreCase = true) == true
                    }
                    _availableDevices.value = insta360Devices
                }
            } catch (e: Exception) {
                Timber.e(e, "Bluetooth search failed")
                _bluetoothStatus.value = BluetoothStatus.ERROR
            } finally {
                _isSearching.value = false
            }
        }
    }

    fun connectDevice(device: BluetoothDevice) {
        viewModelScope.launch {
            try {
                bluetoothManager.connectToDevice(device)
                _bluetoothStatus.value = BluetoothStatus.CONNECTED(device.name ?: "Unknown")
            } catch (e: Exception) {
                Timber.e(e, "Connection failed")
                _bluetoothStatus.value = BluetoothStatus.ERROR
            }
        }
    }

    fun disconnectBluetooth() {
        bluetoothManager.disconnect()
        _bluetoothStatus.value = BluetoothStatus.DISCONNECTED
    }
}
"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(replacement)
print("Done SettingsViewModel")
