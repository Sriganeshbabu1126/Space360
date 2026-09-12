package com.sgbdevapps.space360.service

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCallback
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothProfile
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import android.util.Log
import kotlinx.coroutines.CancellableContinuation
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withTimeoutOrNull
import java.util.UUID
import kotlin.coroutines.resume

data class CameraStatus(
    val isRecording: Boolean,
    val batteryLevel: Int,
    val modelName: String = "Insta360 X4"
)

@SuppressLint("MissingPermission")
class Insta360Controller(private val context: Context) {
    private val TAG = "SPACE360_INSTA360"
    
    // Placeholder UUIDs for Insta360 (replace with actual if available)
    private val SERVICE_UUID = UUID.fromString("0000ffe0-0000-1000-8000-00805f9b34fb")
    private val CHARACTERISTIC_UUID = UUID.fromString("0000ffe1-0000-1000-8000-00805f9b34fb")

    private val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
    val bluetoothAdapter: BluetoothAdapter? = bluetoothManager.adapter
    
    var currentGattConnection: BluetoothGatt? = null
    var currentDevice: BluetoothDevice? = null

    private var connectionContinuation: CancellableContinuation<Boolean>? = null
    private var commandContinuation: CancellableContinuation<ByteArray>? = null

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                if (newState == BluetoothProfile.STATE_CONNECTED) {
                    Log.d(TAG, "Connected to GATT server, starting service discovery")
                    gatt.discoverServices()
                } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                    Log.d(TAG, "Disconnected from GATT server")
                    currentGattConnection?.close()
                    currentGattConnection = null
                    currentDevice = null
                }
            } else {
                Log.e(TAG, "GATT error status: $status")
                connectionContinuation?.takeIf { it.isActive }?.resume(false)
                currentGattConnection?.close()
                currentGattConnection = null
                currentDevice = null
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                Log.d(TAG, "Services discovered successfully")
                connectionContinuation?.takeIf { it.isActive }?.resume(true)
            } else {
                Log.e(TAG, "onServicesDiscovered received: $status")
                connectionContinuation?.takeIf { it.isActive }?.resume(false)
            }
        }

        @Deprecated("Deprecated in Java")
        override fun onCharacteristicWrite(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                Log.d(TAG, "Characteristic written successfully")
                // For simplicity in this mock protocol, assume ACK on write
                commandContinuation?.takeIf { it.isActive }?.resume(byteArrayOf(1))
            } else {
                Log.e(TAG, "Characteristic write failed: $status")
                commandContinuation?.takeIf { it.isActive }?.resume(byteArrayOf(0))
            }
        }

        @Deprecated("Deprecated in Java")
        override fun onCharacteristicRead(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val value = characteristic.value
                commandContinuation?.takeIf { it.isActive }?.resume(value)
            } else {
                commandContinuation?.takeIf { it.isActive }?.resume(byteArrayOf())
            }
        }
    }

    fun scanForCamera(timeout: Long = 10000): Flow<BluetoothDevice> = callbackFlow {
        if (bluetoothAdapter == null || !bluetoothAdapter.isEnabled) {
            close()
            return@callbackFlow
        }

        val scanner = bluetoothAdapter.bluetoothLeScanner
        if (scanner == null) {
            close()
            return@callbackFlow
        }

        val scanCallback = object : ScanCallback() {
            override fun onScanResult(callbackType: Int, result: ScanResult) {
                val device = result.device
                val name = device.name ?: result.scanRecord?.deviceName
                if (name != null && name.contains("Insta360", ignoreCase = true)) {
                    Log.d(TAG, "Found Insta360 camera: $name - ${device.address}")
                    trySend(device)
                }
            }

            override fun onScanFailed(errorCode: Int) {
                Log.e(TAG, "Scan failed with error: $errorCode")
                close(Exception("Scan failed with error: $errorCode"))
            }
        }

        Log.d(TAG, "Starting BLE scan for Insta360 cameras...")
        scanner.startScan(scanCallback)

        // Stop scan after timeout
        kotlinx.coroutines.GlobalScope.launch {
            delay(timeout)
            scanner.stopScan(scanCallback)
            close()
        }

        awaitClose {
            scanner.stopScan(scanCallback)
        }
    }

    suspend fun connectToCamera(device: BluetoothDevice): Boolean {
        Log.d(TAG, "Connecting to camera: ${device.address}")
        currentDevice = device
        
        return withTimeoutOrNull(10000) {
            suspendCancellableCoroutine { cont ->
                connectionContinuation = cont
                currentGattConnection = device.connectGatt(context, false, gattCallback)
                
                cont.invokeOnCancellation {
                    currentGattConnection?.disconnect()
                    currentGattConnection?.close()
                    currentGattConnection = null
                }
            }
        } ?: false
    }

    suspend fun disconnectCamera() {
        Log.d(TAG, "Disconnecting camera")
        currentGattConnection?.disconnect()
        // Wait a bit for the disconnect to propagate before closing
        delay(500)
        currentGattConnection?.close()
        currentGattConnection = null
        currentDevice = null
    }

    private suspend fun sendCommand(command: Byte): ByteArray? {
        val gatt = currentGattConnection ?: return null
        val service = gatt.getService(SERVICE_UUID) ?: return null
        val characteristic = service.getCharacteristic(CHARACTERISTIC_UUID) ?: return null

        characteristic.value = byteArrayOf(command)
        
        return withTimeoutOrNull(5000) {
            suspendCancellableCoroutine { cont ->
                commandContinuation = cont
                val success = gatt.writeCharacteristic(characteristic)
                if (!success) {
                    cont.resume(byteArrayOf())
                }
            }
        }
    }

    suspend fun startRecording(): Result<Unit> {
        Log.d(TAG, "Sending START_RECORDING command (0x01)")
        val response = sendCommand(0x01)
        return if (response != null && response.isNotEmpty() && response[0] == 1.toByte()) {
            Result.success(Unit)
        } else {
            Result.failure(Exception("Failed to start recording"))
        }
    }

    suspend fun stopRecording(): Result<Unit> {
        Log.d(TAG, "Sending STOP_RECORDING command (0x02)")
        val response = sendCommand(0x02)
        return if (response != null && response.isNotEmpty() && response[0] == 1.toByte()) {
            Result.success(Unit)
        } else {
            Result.failure(Exception("Failed to stop recording"))
        }
    }

    suspend fun getDeviceStatus(): Result<CameraStatus> {
        Log.d(TAG, "Sending GET_STATUS command (0x03)")
        val response = sendCommand(0x03)
        return if (response != null && response.isNotEmpty()) {
            // Mock parsing logic
            val isRec = response.size > 1 && response[1] == 1.toByte()
            val batt = if (response.size > 2) response[2].toInt() else 100
            Result.success(CameraStatus(isRecording = isRec, batteryLevel = batt))
        } else {
            Result.failure(Exception("Failed to get camera status"))
        }
    }

    suspend fun getBatteryLevel(): Result<Int> {
        Log.d(TAG, "Sending GET_BATTERY command (0x04)")
        val response = sendCommand(0x04)
        return if (response != null && response.isNotEmpty()) {
            val batt = if (response.size > 1) response[1].toInt() else 100
            Result.success(batt)
        } else {
            Result.failure(Exception("Failed to get battery level"))
        }
    }
}
