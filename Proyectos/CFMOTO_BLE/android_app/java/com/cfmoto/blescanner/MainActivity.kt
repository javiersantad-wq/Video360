package com.cfmoto.blescanner

import android.Manifest
import android.bluetooth.BluetoothGattService
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.IBinder
import android.util.Log
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.gson.GsonBuilder
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {
    companion object {
        private const val TAG = "MainActivity"
        private const val REQUEST_PERMISSIONS = 1001
        private val REQUIRED_PERMISSIONS = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            arrayOf(Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT, Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.POST_NOTIFICATIONS)
        } else {
            arrayOf(Manifest.permission.BLUETOOTH, Manifest.permission.BLUETOOTH_ADMIN, Manifest.permission.ACCESS_FINE_LOCATION)
        }
    }

    private lateinit var bleScanner: BleScanner
    private lateinit var bleManager: BleManager
    private lateinit var adapter: DeviceAdapter

    private var tvStatus: TextView? = null
    private var tvDeviceCount: TextView? = null
    private var tvLog: TextView? = null
    private var btnScan: Button? = null
    private var recyclerDevices: RecyclerView? = null
    private var btnSniffer: Button? = null

    private val devices = mutableListOf<BleScanner.BleDevice>()
    private val connectionLogs = mutableListOf<String>()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.US)
    private val gson = GsonBuilder().setPrettyPrinting().create()

    private var discoveredServices: List<BluetoothGattService> = emptyList()

    // Sniffer service
    private var snifferService: BleSnifferService? = null
    private var isSnifferRunning = false
    private var serviceBound = false

    private val serviceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            val binder = service as BleSnifferService.LocalBinder
            snifferService = binder.getService()
            serviceBound = true
            appendLog("Sniffer service conectado")
            updateSnifferButton()
        }
        override fun onServiceDisconnected(name: ComponentName?) {
            snifferService = null
            serviceBound = false
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        bleScanner = BleScanner(this)
        bleManager = BleManager(this)
        initViews()
        updateStatus()
        checkPermissions()
        
        // Bind to sniffer service
        Intent(this, BleSnifferService::class.java).also { intent ->
            bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE)
        }
    }

    private fun initViews() {
        tvStatus = findViewById(R.id.tv_status)
        tvDeviceCount = findViewById(R.id.tv_device_count)
        tvLog = findViewById(R.id.tv_log)
        btnScan = findViewById(R.id.btn_scan)
        recyclerDevices = findViewById(R.id.recycler_devices)
        btnSniffer = findViewById(R.id.btn_sniffer)
        recyclerDevices?.layoutManager = LinearLayoutManager(this)
        adapter = DeviceAdapter(devices) { device -> showDeviceDetail(device) }
        recyclerDevices?.adapter = adapter
        btnScan?.setOnClickListener { if (bleScanner.isScanning()) stopScan() else startScan() }
        btnSniffer?.setOnClickListener { toggleSniffer() }
        findViewById<Button>(R.id.btn_save)?.setOnClickListener { saveLog() }
        findViewById<Button>(R.id.btn_clear)?.setOnClickListener { clearLog() }
        findViewById<Button>(R.id.btn_export)?.setOnClickListener { exportJson() }
    }

    private fun checkPermissions(): Boolean {
        val missing = REQUIRED_PERMISSIONS.filter { ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }
        if (missing.isNotEmpty()) { ActivityCompat.requestPermissions(this, missing.toTypedArray(), REQUEST_PERMISSIONS); return false }
        return true
    }

    private fun startScan() {
        if (!checkPermissions()) { appendLog("Permission required"); return }
        if (!bleScanner.hasBleSupport()) { appendLog("BLE not supported"); return }
        if (!bleScanner.isBluetoothEnabled()) { appendLog("Bluetooth is OFF"); showBluetoothOffDialog(); return }
        devices.clear()
        adapter.notifyDataSetChanged()
        updateStatus()
        appendLog("Starting BLE scan...")
        bleScanner.startScan(object : BleScanner.BleScanCallback {
            override fun onDeviceFound(device: BleScanner.BleDevice) {
                runOnUiThread {
                    val existing = devices.indexOfFirst { it.address == device.address }
                    if (existing >= 0) { devices[existing] = device; adapter.notifyItemChanged(existing) }
                    else { devices.add(device); adapter.notifyItemInserted(devices.size - 1) }
                    val flag = if (device.isCfMoto) " [CFMOTO]" else ""
                    appendLog("Found: ${device.name ?: "Unknown"}$flag (${device.rssi} dBm)")
                    tvDeviceCount?.text = "${devices.size} devices"
                }
            }
            override fun onScanStarted() { runOnUiThread { btnScan?.text = getString(R.string.stop_scan); tvStatus?.text = getString(R.string.status_scanning) } }
            override fun onScanStopped() { runOnUiThread { btnScan?.text = getString(R.string.start_scan); tvStatus?.text = "Scan complete - ${devices.size} devices found"; appendLog("Scan stopped") } }
            override fun onScanError(error: String) { runOnUiThread { appendLog("Error: $error"); btnScan?.text = getString(R.string.start_scan) } }
        })
    }

    private fun stopScan() { bleScanner.stopScan() }

    private fun showDeviceDetail(device: BleScanner.BleDevice) {
        appendLog("Connecting to ${device.name ?: "Unknown"} (${device.address})...")
        bleManager.connect(device.address, object : BleManager.ConnectionCallback {
            override fun onConnected() { runOnUiThread { appendLog("Connected!") } }
            override fun onDisconnected() { runOnUiThread { appendLog("Disconnected") } }
            override fun onServicesDiscovered(services: List<BluetoothGattService>) {
                runOnUiThread {
                    discoveredServices = services
                    appendLog("${services.size} services discovered")
                    showServicesDialog(services)
                }
            }
            override fun onCharacteristicRead(uuid: UUID, value: ByteArray) { runOnUiThread { appendLog("Read ${value.toHexString()} from $uuid") } }
            override fun onCharacteristicWritten(uuid: UUID, value: ByteArray) { runOnUiThread { appendLog("Written to $uuid") } }
            override fun onError(error: String) { runOnUiThread { appendLog("Error: $error") } }
        })
    }

    private fun showServicesDialog(services: List<BluetoothGattService>) {
        val serviceInfos = services.mapIndexed { idx, service ->
            val chars = service.characteristics.map { char ->
                val props = char.properties
                val readable = props and 2 != 0
                val writable = props and 6 != 0
                val notifiable = props and 32 != 0
                "  ${char.uuid}\n    props:${char.properties} ${if (readable) "R" else ""}${if (writable) "W" else ""}${if (notifiable) "N" else ""}"
            }.joinToString("\n")
            "${idx + 1}. Service: ${service.uuid}\n$chars"
        }.joinToString("\n\n")

        val hasNus = services.any { it.uuid.toString().equals("0000fea1-0000-1000-8000-00805f9b34fb", ignoreCase = true) }

        val items = if (hasNus) arrayOf("Read All Characteristics", "Read Each Characteristic", "Enable UART Notifications", "Disconnect") 
                   else arrayOf("Read All Characteristics", "Read Each Characteristic", "Disconnect")

        AlertDialog.Builder(this)
            .setTitle("GATT Services (${services.size})")
            .setMessage(serviceInfos)
            .setItems(items) { _, which ->
                when {
                    items[which] == "Read All Characteristics" -> readAllCharacteristics(services)
                    items[which] == "Read Each Characteristic" -> showReadCharacteristicsDialog(services)
                    items[which] == "Enable UART Notifications" -> enableUartNotifications(services)
                    items[which] == "Disconnect" -> bleManager.disconnect()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun readAllCharacteristics(services: List<BluetoothGattService>) {
        var readCount = 0
        for (service in services) {
            for (char in service.characteristics) {
                if (char.properties and 2 != 0) {
                    bleManager.readCharacteristic(service.uuid, char.uuid)
                    readCount++
                }
            }
        }
        appendLog("Started reading $readCount characteristics")
    }

    private fun showReadCharacteristicsDialog(services: List<BluetoothGattService>) {
        val allChars = mutableListOf<Triple<String, UUID, UUID>>()
        for (service in services) {
            for (char in service.characteristics) {
                val props = char.properties
                val readable = props and 2 != 0
                val writable = props and 6 != 0
                val displayName = "${char.uuid}\n  S:${service.uuid}\n  ${if (readable) "R" else ""}${if (writable) "W" else ""}"
                allChars.add(Triple(displayName, service.uuid, char.uuid))
            }
        }
        val items = allChars.map { it.first }.toTypedArray()
        val checked = BooleanArray(items.size) { false }
        AlertDialog.Builder(this)
            .setTitle("Select Characteristics to Read")
            .setMultiChoiceItems(items, checked) { _, which, isChecked -> checked[which] = isChecked }
            .setPositiveButton("Read Selected") { _, _ ->
                for (i in checked.indices) {
                    if (checked[i]) {
                        val (_, svc, char) = allChars[i]
                        bleManager.readCharacteristic(svc, char)
                    }
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun enableUartNotifications(services: List<BluetoothGattService>) {
        val nusService = services.find {
            it.uuid.toString().equals("0000fea1-0000-1000-8000-00805f9b34fb", ignoreCase = true)
        } ?: return
        for (char in nusService.characteristics) {
            val uuidStr = char.uuid.toString().lowercase()
            if (uuidStr.endsWith("0002") || uuidStr.endsWith("0003")) {
                if (char.properties and 32 != 0) {
                    bleManager.enableNotification(nusService.uuid, char.uuid)
                    appendLog("Enabled notifications on ${char.uuid}")
                }
            }
        }
        for (char in nusService.characteristics) {
            if (char.properties and 2 != 0) bleManager.readCharacteristic(nusService.uuid, char.uuid)
        }
        for (char in nusService.characteristics) {
            if (char.properties and 8 != 0) {
                val query = byteArrayOf(0x01, 0x03, 0x00, 0x00)
                bleManager.writeCharacteristic(nusService.uuid, char.uuid, query)
                appendLog("Sent query to ${char.uuid}")
            }
        }
    }

    private fun toggleSniffer() {
        if (!checkPermissions()) { appendLog("Permission required"); return }
        if (!bleScanner.isBluetoothEnabled()) { appendLog("Bluetooth is OFF"); showBluetoothOffDialog(); return }
        
        if (isSnifferRunning) {
            stopSnifferMode()
        } else {
            startSnifferMode()
        }
    }

    private fun startSnifferMode() {
        appendLog("Iniciando modo Sniffer...")
        val intent = Intent(this, BleSnifferService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        isSnifferRunning = true
        updateSnifferButton()
        appendLog("Sniffer activo en segundo plano")
        
        // Also start foreground scan
        if (!bleScanner.isScanning()) {
            devices.clear()
            adapter.notifyDataSetChanged()
            bleScanner.startScan(object : BleScanner.BleScanCallback {
                override fun onDeviceFound(device: BleScanner.BleDevice) {
                    runOnUiThread {
                        val existing = devices.indexOfFirst { it.address == device.address }
                        if (existing >= 0) { devices[existing] = device; adapter.notifyItemChanged(existing) }
                        else { devices.add(device); adapter.notifyItemInserted(devices.size - 1) }
                        val flag = if (device.isCfMoto) " [CFMOTO]" else ""
                        appendLog("Found: ${device.name ?: "Unknown"}$flag (${device.rssi} dBm)")
                        tvDeviceCount?.text = "${devices.size} devices"
                    }
                }
                override fun onScanStarted() { runOnUiThread { btnScan?.text = getString(R.string.stop_scan); tvStatus?.text = "Sniffer + Scan activo" } }
                override fun onScanStopped() { runOnUiThread { btnScan?.text = getString(R.string.start_scan); tvStatus?.text = "Sniffer activo - esperando moto..." } }
                override fun onScanError(error: String) { runOnUiThread { appendLog("Error: $error") } }
            })
        }
    }

    private fun stopSnifferMode() {
        snifferService?.stopSniffing()
        isSnifferRunning = false
        if (bleScanner.isScanning()) bleScanner.stopScan()
        updateSnifferButton()
        appendLog("Sniffer detenido")
    }

    private fun updateSnifferButton() {
        runOnUiThread {
            btnSniffer?.text = if (isSnifferRunning) "Detener Sniffer" else "Sniffer"
            btnSniffer?.setBackgroundColor(
                if (isSnifferRunning) 
                    ContextCompat.getColor(this, android.R.color.holo_red_dark) 
                else 
                    ContextCompat.getColor(this, android.R.color.holo_green_dark)
            )
        }
    }

    private fun showBluetoothOffDialog() { AlertDialog.Builder(this).setTitle("Bluetooth Off").setMessage("Turn on Bluetooth").setPositiveButton("OK", null).show() }
    private fun updateStatus() { tvStatus?.text = if (bleScanner.isScanning()) getString(R.string.status_scanning) else getString(R.string.status_ready); tvDeviceCount?.text = "${devices.size} devices" }

    private fun appendLog(message: String) {
        val sdf = SimpleDateFormat("HH:mm:ss", Locale.US)
        val logEntry = "[${sdf.format(Date())}] $message"
        connectionLogs.add(logEntry)
        tvLog?.text = connectionLogs.takeLast(6).joinToString("\n")
        Log.d(TAG, logEntry)
    }

    private fun saveLog() {
        try {
            val file = File(getExternalFilesDir(null), "cfmoto_scan_${dateFormat.format(Date())}.txt")
            FileWriter(file).use { it.write(connectionLogs.joinToString("\n")) }
            Toast.makeText(this, "Saved: ${file.absolutePath}", Toast.LENGTH_LONG).show()
            appendLog("Log saved to ${file.name}")
        } catch (e: Exception) { Toast.makeText(this, "Save failed: ${e.message}", Toast.LENGTH_SHORT).show() }
    }

    private fun clearLog() { connectionLogs.clear(); tvLog?.text = "" }

    private fun exportJson() {
        try {
            // Include sniffer data if running
            val allLogs = connectionLogs.toMutableList()
            if (isSnifferRunning && serviceBound) {
                val snifferData = snifferService?.getCaptureLog() ?: emptyList()
                appendLog("Exportando ${snifferData.size} entradas del sniffer...")
                val file = File(getExternalFilesDir(null), "cfmoto_sniffer_${dateFormat.format(Date())}.json")
                FileWriter(file).use { it.write(snifferService?.exportJson() ?: "{}") }
                Toast.makeText(this, "Exported: ${file.absolutePath}", Toast.LENGTH_LONG).show()
                appendLog("Exported ${snifferData.size} sniffer entries")
            }
            
            val file = File(getExternalFilesDir(null), "cfmoto_devices_${dateFormat.format(Date())}.json")
            FileWriter(file).use { it.write(gson.toJson(devices)) }
            Toast.makeText(this, "Exported: ${file.absolutePath}", Toast.LENGTH_LONG).show()
            appendLog("Exported ${devices.size} devices")
        } catch (e: Exception) { Toast.makeText(this, "Export failed: ${e.message}", Toast.LENGTH_SHORT).show() }
    }

    override fun onDestroy() {
        super.onDestroy()
        bleScanner.stopScan()
        bleManager.disconnect()
        if (serviceBound) {
            snifferService?.stopSniffing()
            unbindService(serviceConnection)
            serviceBound = false
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_PERMISSIONS) {
            if (grantResults.all { it == PackageManager.PERMISSION_GRANTED }) { appendLog("Permissions granted"); startScan() }
            else { appendLog("Permissions denied") }
        }
    }

    private fun ByteArray.toHexString(): String = joinToString("") { "%02X".format(it) }
}