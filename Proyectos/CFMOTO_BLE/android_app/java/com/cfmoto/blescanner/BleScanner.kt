package com.cfmoto.blescanner

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCallback
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothGattService
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothProfile
import android.bluetooth.le.BluetoothLeScanner
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanRecord
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.os.PersistableBundle
import android.util.Log
import android.util.SparseArray
import java.text.SimpleDateFormat
import java.util.*

class BleScanner(private val context: Context) {
    companion object {
        private const val TAG = "BleScanner"
        private const val SCAN_PERIOD = 30000L
        // CFMOTO 300NK 2025 Mexico - Bluetooth device name filters
        private val CFMOTO_FILTER_NAMES = listOf(
            "CFMOTO", "CFM", "CF", "MOTAN",
            // CFMOTO NK series (naked bikes)
            "NK", "NK300", "300NK", "250NK", "150NK",
            // CFMOTO CF series models
            "CF300", "CF250", "CF150", "CF125",
            // Additional CFMOTO naming patterns
            "CFX", "CFR", "CFS",
            // Specific observed BLE names from 300NK
            "CFMOTO-LE-", "CFMOTO-5F2C"
        )
        // Known CFMOTO BLE MAC prefixes (partial match, case-insensitive)
        private val CFMOTO_MAC_PREFIXES = listOf(
            "DD:0D:30",  // CFMOTO-LE-8C472C
            "03:FF:01"   // CFMOTO-5F2C
        )
        // Nordic UART Service - used by CFMOTO BLE module
        private val CFMOTO_SERVICE_UUIDS = listOf(
            "0000fea1-0000-1000-8000-00805f9b34fb"  // Nordic UART TX
        )
    }

    interface BleScanCallback {
        fun onDeviceFound(device: BleDevice)
        fun onScanStarted()
        fun onScanStopped()
        fun onScanError(error: String)
    }

    data class BleDevice(
        val name: String?,
        val address: String,
        val rssi: Int,
        val manufacturerData: Map<Int, ByteArray>,
        val serviceUuids: List<UUID>,
        val isCfMoto: Boolean,
        val timestamp: Long = System.currentTimeMillis()
    )

    private var bluetoothAdapter: BluetoothAdapter? = null

    init {
        val bm = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothAdapter = bm.adapter
    }
    private var scanner: BluetoothLeScanner? = null
    private var scanCallback: BleScanCallback? = null
    private var isScanning = false
    private val handler = Handler(Looper.getMainLooper())
    private val foundDevices = mutableListOf<BleDevice>()

    fun isBluetoothEnabled(): Boolean = bluetoothAdapter?.isEnabled == true
    fun isScanning(): Boolean = isScanning
    fun hasBleSupport(): Boolean = context.packageManager.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH_LE)
    fun getDevices(): List<BleDevice> = foundDevices.toList()

    @SuppressLint("MissingPermission")
    fun startScan(callback: BleScanCallback) {
        if (!hasBleSupport()) { callback.onScanError("BLE not supported"); return }
        if (!isBluetoothEnabled()) { callback.onScanError("Bluetooth is OFF"); return }
        this.scanCallback = callback
        foundDevices.clear()
        scanner = bluetoothAdapter?.bluetoothLeScanner
        try {
            val scanSettings = ScanSettings.Builder()
                .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                .build()
            scanner?.startScan(null, scanSettings, androidScanCallback)
            isScanning = true
            callback.onScanStarted()
            handler.postDelayed({ stopScan() }, SCAN_PERIOD)
            Log.d(TAG, "Scan started")
        } catch (e: Exception) { callback.onScanError("Error: ${e.message}") }
    }

    @SuppressLint("MissingPermission")
    fun stopScan() {
        if (!isScanning) return
        try {
            scanner?.stopScan(androidScanCallback)
            isScanning = false
            scanCallback?.onScanStopped()
        } catch (e: Exception) { }
    }

    private val androidScanCallback = object : ScanCallback() {
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            try {
                val device = result.device
                val rssi = result.rssi
                val name = device.name ?: result.scanRecord?.deviceName

                val manufacturerData = mutableMapOf<Int, ByteArray>()
                val record: ScanRecord? = result.scanRecord
                if (record != null) {
                    try {
                        val mfgField = ScanRecord::class.java.getDeclaredMethod("getManufacturerData")
                        @Suppress("UNCHECKED_CAST")
                        val mfgData = mfgField.invoke(record) as? SparseArray<ByteArray>
                        if (mfgData != null) {
                            for (i in 0 until mfgData.size()) {
                                manufacturerData[mfgData.keyAt(i)] = mfgData.valueAt(i)
                            }
                        }
                    } catch (e: Exception) {
                        // Try alternative approach
                        val bytes = record.bytes
                        if (bytes != null) {
                            parseManufacturerData(bytes, manufacturerData)
                        }
                    }
                }

                val serviceUuids = record?.serviceUuids?.map { it.uuid } ?: emptyList()

                // Check if device is a CFMOTO using multiple criteria
                val nameMatchesCfMoto = name?.let { n -> CFMOTO_FILTER_NAMES.any { n.uppercase().contains(it) } } ?: false
                val macMatchesCfMoto = CFMOTO_MAC_PREFIXES.any { prefix -> device.address.uppercase().startsWith(prefix.uppercase()) }
                val hasCfMotoService = serviceUuids.any { uuid -> CFMOTO_SERVICE_UUIDS.any { it.equals(uuid.toString(), ignoreCase = true) } }
                val isCfMoto = nameMatchesCfMoto || macMatchesCfMoto || hasCfMotoService

                val bleDevice = BleDevice(name, device.address, rssi, manufacturerData, serviceUuids, isCfMoto)

                if (foundDevices.none { it.address == device.address }) {
                    foundDevices.add(bleDevice)
                    scanCallback?.onDeviceFound(bleDevice)
                    Log.d(TAG, "Found: ${name ?: "Unknown"}${if (isCfMoto) " [CFMOTO]" else ""} ${device.address} RSSI:$rssi")
                }
            } catch (e: Exception) { Log.e(TAG, "Error: ${e.message}") }
        }

        override fun onScanFailed(errorCode: Int) {
            val msg = "Scan failed (code: $errorCode)"
            scanCallback?.onScanError(msg)
        }

        override fun onBatchScanResults(results: List<ScanResult>) {
            results.forEach { onScanResult(ScanSettings.CALLBACK_TYPE_ALL_MATCHES, it) }
        }
    }

    private fun parseManufacturerData(bytes: ByteArray, manufacturerData: MutableMap<Int, ByteArray>) {
        var i = 0
        while (i < bytes.size - 1) {
            if (bytes[i].toInt() == 0xFF && i + 3 < bytes.size) {
                val companyId = (bytes[i + 1].toInt() and 0xFF) or ((bytes[i + 2].toInt() and 0xFF) shl 8)
                val len = bytes[i + 3].toInt() and 0xFF
                if (i + 4 + len <= bytes.size) {
                    val data = bytes.copyOfRange(i + 4, i + 4 + len)
                    manufacturerData[companyId] = data
                }
                i += 4 + len
            } else {
                i++
            }
        }
    }
}