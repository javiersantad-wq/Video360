package com.cfmoto.blescanner

import android.app.*
import android.bluetooth.*
import android.content.Context
import android.content.Intent
import android.os.*
import android.util.Log
import java.text.SimpleDateFormat
import java.util.*

class BleSnifferService : Service() {
    companion object {
        private const val TAG = "BleSnifferService"
        private const val NOTIFY_ID = 1001
        private const val CHANNEL_ID = "cfmoto_sniffer"
    }

    private val binder = LocalBinder()
    private lateinit var vibrator: Vibrator
    private val handler = Handler(Looper.getMainLooper())
    private var bluetoothAdapter: BluetoothAdapter? = null
    private var gatt: BluetoothGatt? = null
    private var isSniffing = false

    // Capture log
    private val captureLog = mutableListOf<CaptureEntry>()
    data class CaptureEntry(
        val timestamp: Long,
        val direction: String, // "TX"=phone to bike, "RX"=bike to phone
        val serviceUuid: String,
        val charUuid: String,
        val hexData: String,
        val description: String
    )

    inner class LocalBinder : Binder() { fun getService() = this@BleSnifferService }

    override fun onCreate() {
        super.onCreate()
        val bm = getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothAdapter = bm.adapter
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = buildNotification("Sniffer activo", "Esperando moto...")
        startForeground(NOTIFY_ID, notification)
        return START_STICKY
    }

    override fun onBind(intent: Intent): IBinder = binder

    override fun onDestroy() { stopSniffing(); super.onDestroy() }

    fun startSniffing() {
        if (isSniffing) return
        // Scan for CFMOTO devices
        val scanner = bluetoothAdapter?.bluetoothLeScanner
        val settings = android.bluetooth.le.ScanSettings.Builder()
            .setScanMode(android.bluetooth.le.ScanSettings.SCAN_MODE_LOW_LATENCY)
            .build()
        
        val filter = android.bluetooth.le.ScanFilter.Builder()
            .setDeviceName("CFMOTO-LE-8C472C")
            .build()

        try {
            scanner?.startScan(listOf(filter), settings, scanCallback)
            isSniffing = true
            addLog("TX", "SCANNER", "SCANNER", "SYSTEM", "Scan iniciado")
        } catch (e: SecurityException) {
            Log.e(TAG, "Scan error: $e")
        }
    }

    fun stopSniffing() {
        try {
            bluetoothAdapter?.bluetoothLeScanner?.stopScan(scanCallback)
        } catch (e: SecurityException) { }
        gatt?.disconnect()
        gatt = null
        isSniffing = false
        addLog("TX", "SCANNER", "SCANNER", "SYSTEM", "Scan detenido")
    }

    private val scanCallback = object : android.bluetooth.le.ScanCallback() {
        override fun onScanResult(callbackType: Int, result: android.bluetooth.le.ScanResult) {
            val device = result.device
            val name = device.name ?: "Unknown"
            val rssi = result.rssi
            addLog("TX", "SCANNER", "SCANNER", "FOUND", "Device: $name ($rssi dBm) ${device.address}")
            
            // Auto-connect to CFMOTO-LE-8C472C or CFMOTO-5F2C
            if (name.contains("CFMOTO-LE-") || name.contains("CFMOTO-5F2C") || 
                device.address.startsWith("DD:0D:30", ignoreCase = true) ||
                device.address.startsWith("03:FF:01", ignoreCase = true)) {
                handler.post {
                    updateNotification("Conectando a $name...")
                    try {
                        bluetoothAdapter?.bluetoothLeScanner?.stopScan(this)
                    } catch (e: SecurityException) { }
                    connectToDevice(device)
                }
            }
        }

        override fun onBatchScanResults(results: MutableList<android.bluetooth.le.ScanResult>) {
            for (r in results) onScanResult(0, r)
        }

        override fun onScanFailed(errorCode: Int) {
            addLog("TX", "SCANNER", "SCANNER", "ERROR", "Scan falló: $errorCode")
        }
    }

    private fun connectToDevice(device: BluetoothDevice) {
        addLog("TX", "GATT", "CONN", "CONNECT", "Conectando a ${device.address}")
        try {
            gatt = device.connectGatt(this, false, gattCallback, BluetoothDevice.TRANSPORT_LE)
        } catch (e: SecurityException) {
            addLog("TX", "GATT", "CONN", "ERROR", "Permiso denegado: $e")
        }
    }

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            when (newState) {
                BluetoothProfile.STATE_CONNECTED -> {
                    handler.post {
                        addLog("RX", "GATT", "CONN", "CONNECTED", "Conectado al GATT server")
                        updateNotification("Conectado - descubriendo servicios...")
                        try { gatt.discoverServices() } catch (e: SecurityException) { }
                    }
                }
                BluetoothProfile.STATE_DISCONNECTED -> handler.post {
                    addLog("RX", "GATT", "CONN", "DISCONNECTED", "Desconectado")
                    updateNotification("Desconectado - reintentando...")
                    // Auto-reconnect after 3 seconds
                    handler.postDelayed({ 
                        if (isSniffing) startSniffing() 
                    }, 3000)
                }
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                handler.post {
                    val services = gatt.services
                    addLog("RX", "GATT", "SVC", "DISCOVERED", "Descubiertos ${services.size} servicios")
                    for (svc in services) {
                        addLog("RX", "GATT", "SERVICE", svc.uuid.toString(), "Service")
                        for (char in svc.characteristics) {
                            val props = char.properties
                            val desc = "Char props:${char.properties} " +
                                if (props and 2 != 0) "R " else "" +
                                if (props and 6 != 0) "W " else "" +
                                if (props and 32 != 0) "N " else ""
                            addLog("RX", svc.uuid.toString(), char.uuid.toString(), "CHAR_DESC", desc)
                            
                            // Enable notifications for all notifiable characteristics
                            if (props and 32 != 0) {
                                try {
                                    gatt.setCharacteristicNotification(char, true)
                                    val desc2 = char.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"))
                                    desc2?.let {
                                        it.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                                        gatt.writeDescriptor(it)
                                    }
                                    addLog("TX", svc.uuid.toString(), char.uuid.toString(), "NOTIFY", "Notificaciones habilitadas")
                                } catch (e: SecurityException) { }
                            }
                            
                            // Read all readable characteristics
                            if (props and 2 != 0) {
                                try { gatt.readCharacteristic(char) } catch (e: SecurityException) { }
                            }
                        }
                    }
                    updateNotification("Capturando ${services.size} servicios")
                }
            }
        }

        override fun onCharacteristicRead(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val hex = characteristic.value?.toHexString() ?: "null"
                val svc = characteristic.service.uuid.toString()
                val char = characteristic.uuid.toString()
                handler.post {
                    addLog("RX", svc, char, "READ", hex)
                    // Vibrate on activity
                    vibrate(50)
                }
            }
        }

        override fun onCharacteristicWrite(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) {
            val hex = characteristic.value?.toHexString() ?: "null"
            val svc = characteristic.service.uuid.toString()
            val char = characteristic.uuid.toString()
            handler.post {
                addLog("TX", svc, char, "WRITE", hex)
                vibrate(30)
            }
        }

        override fun onCharacteristicChanged(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic) {
            val hex = characteristic.value?.toHexString() ?: "null"
            val svc = characteristic.service.uuid.toString()
            val char = characteristic.uuid.toString()
            handler.post {
                addLog("RX", svc, char, "NOTIFY", hex)
                vibrate(20)
            }
        }

        override fun onDescriptorWrite(gatt: BluetoothGatt, descriptor: BluetoothGattDescriptor, status: Int) {
            val hex = descriptor.value?.toHexString() ?: "null"
            val svc = descriptor.characteristic.service.uuid.toString()
            val char = descriptor.characteristic.uuid.toString()
            handler.post {
                addLog("TX", svc, char, "DESC_WRITE", hex)
            }
        }

        override fun onReadRemoteRssi(gatt: BluetoothGatt, rssi: Int, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                handler.post { addLog("RX", "GATT", "RSSI", "RSSI", "Signal: $rssi dBm") }
            }
        }
    }

    private fun addLog(direction: String, service: String, char: String, type: String, data: String) {
        val entry = CaptureEntry(System.currentTimeMillis(), direction, service, char, data, type)
        captureLog.add(entry)
        Log.d(TAG, "[$direction] $service/$char $type: $data")
    }

    private fun vibrate(durationMs: Long) {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vib = getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
                vib?.vibrate(VibrationEffect.createOneShot(durationMs, VibrationEffect.DEFAULT_AMPLITUDE))
            }
        } catch (e: Exception) { }
    }

    fun getCaptureLog(): List<CaptureEntry> = captureLog.toList()

    fun exportLog(): String {
        val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.US)
        return buildString {
            appendLine("# CFMOTO BLE Capture Log")
            appendLine("# Date: ${sdf.format(Date())}")
            appendLine("# Entries: ${captureLog.size}")
            appendLine("#")
            appendLine("# Direction | Timestamp | Service | Characteristic | Type | Data (Hex)")
            appendLine("#-----------|-----------|---------|---------------|------|-------------")
            for (e in captureLog) {
                appendLine("${e.direction} | ${sdf.format(Date(e.timestamp))} | ${e.serviceUuid} | ${e.charUuid} | ${e.description} | ${e.hexData}")
            }
        }
    }

    fun exportJson(): String {
        val gson = com.google.gson.GsonBuilder().setPrettyPrinting().create()
        return gson.toJson(captureLog.map {
            mapOf(
                "timestamp" to it.timestamp,
                "direction" to it.direction,
                "serviceUuid" to it.serviceUuid,
                "charUuid" to it.charUuid,
                "hex" to it.hexData,
                "type" to it.description
            )
        })
    }

    fun clearLog() { captureLog.clear() }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(CHANNEL_ID, "CFMOTO Sniffer", NotificationManager.IMPORTANCE_LOW).apply {
                description = "Background BLE sniffer for CFMOTO"
            }
            val nm = getSystemService(NotificationManager::class.java)
            nm.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(title: String, text: String): Notification {
        return Notification.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_search)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(text: String) {
        val nm = getSystemService(NotificationManager::class.java)
        nm.notify(NOTIFY_ID, buildNotification("CFMOTO Sniffer", text))
    }

    private fun ByteArray.toHexString(): String = joinToString("") { "%02X".format(it) }
}