package com.cfmoto.blescanner

import android.annotation.SuppressLint
import android.bluetooth.*
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.util.Log
import java.text.SimpleDateFormat
import java.util.*

class BleManager(private val context: Context) {
    companion object { private const val TAG = "BleManager" }

    interface ConnectionCallback {
        fun onConnected()
        fun onDisconnected()
        fun onServicesDiscovered(services: List<BluetoothGattService>)
        fun onCharacteristicRead(uuid: UUID, value: ByteArray)
        fun onCharacteristicWritten(uuid: UUID, value: ByteArray)
        fun onError(error: String)
    }

    private val bluetoothAdapter: BluetoothAdapter? by lazy {
        val bm = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        bm.adapter
    }

    private var gatt: BluetoothGatt? = null
    private var connectionCallback: ConnectionCallback? = null
    private val handler = Handler(Looper.getMainLooper())
    val connectionLogs = mutableListOf<String>()

    @SuppressLint("MissingPermission")
    fun connect(address: String, callback: ConnectionCallback) {
        this.connectionCallback = callback
        addLog("Connecting to $address...")
        try {
            val device = bluetoothAdapter?.getRemoteDevice(address) ?: run { callback.onError("Device not found"); return }
            gatt = device.connectGatt(context, false, gattCallback, BluetoothDevice.TRANSPORT_LE)
            addLog("GATT connection initiated")
        } catch (e: SecurityException) { callback.onError("Permission denied") }
    }

    @SuppressLint("MissingPermission")
    fun disconnect() {
        try {
            gatt?.disconnect()
            gatt?.close()
            gatt = null
            addLog("Disconnected")
        } catch (e: SecurityException) { }
    }

    @SuppressLint("MissingPermission")
    fun discoverServices() {
        try { addLog("Discovering services..."); gatt?.discoverServices() } catch (e: SecurityException) { connectionCallback?.onError("Permission denied") }
    }

    @SuppressLint("MissingPermission")
    fun readCharacteristic(serviceUuid: UUID, charUuid: UUID) {
        try { gatt?.getService(serviceUuid)?.getCharacteristic(charUuid)?.let { gatt?.readCharacteristic(it); addLog("Reading $charUuid") } } catch (e: SecurityException) { connectionCallback?.onError("Permission denied") }
    }

    @SuppressLint("MissingPermission")
    fun writeCharacteristic(serviceUuid: UUID, charUuid: UUID, data: ByteArray) {
        try {
            gatt?.getService(serviceUuid)?.getCharacteristic(charUuid)?.let { char ->
                char.value = data
                char.writeType = BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT
                gatt?.writeCharacteristic(char)
                addLog("Writing ${data.toHexString()} to $charUuid")
            }
        } catch (e: SecurityException) { connectionCallback?.onError("Permission denied") }
    }

    // Enable notifications for a characteristic
    @SuppressLint("MissingPermission")
    fun enableNotification(serviceUuid: UUID, charUuid: UUID) {
        try {
            val char = gatt?.getService(serviceUuid)?.getCharacteristic(charUuid) ?: return
            gatt?.setCharacteristicNotification(char, true)
            val descriptor = char.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"))
            descriptor?.let {
                it.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                gatt?.writeDescriptor(it)
                addLog("Enabled notifications for $charUuid")
            }
        } catch (e: SecurityException) { connectionCallback?.onError("Permission denied") }
    }

    fun getServices(): List<BluetoothGattService> = gatt?.services ?: emptyList()

    private fun addLog(msg: String) {
        val sdf = SimpleDateFormat("HH:mm:ss.SSS", Locale.US)
        val log = "[${sdf.format(Date())}] $msg"
        connectionLogs.add(log)
        Log.d(TAG, log)
    }

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            when (newState) {
                BluetoothProfile.STATE_CONNECTED -> {
                    handler.post {
                        addLog("Connected to GATT server")
                        connectionCallback?.onConnected()
                        // Auto-discover services
                        addLog("Discovering services...")
                        gatt.discoverServices()
                    }
                }
                BluetoothProfile.STATE_DISCONNECTED -> handler.post {
                    addLog("Disconnected")
                    connectionCallback?.onDisconnected()
                    gatt?.close()
                }
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                handler.post {
                    val services = gatt.services
                    addLog("Discovered ${services.size} services")
                    // Log each service and its characteristics
                    for (service in services) {
                        addLog("Service: ${service.uuid}")
                        for (char in service.characteristics) {
                            val props = char.properties
                            val readable = props and 2 != 0
                            val writable = props and 6 != 0
                            val notifiable = props and 32 != 0
                            addLog("  Char: ${char.uuid} props:${char.properties} ${if (readable) "R" else ""}${if (writable) "W" else ""}${if (notifiable) "N" else ""}")
                        }
                    }
                    connectionCallback?.onServicesDiscovered(services)
                }
            } else {
                handler.post { connectionCallback?.onError("Service discovery failed (status: $status)") }
            }
        }

        override fun onCharacteristicRead(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                handler.post {
                    val value = characteristic.value
                    addLog("Read ${value?.toHexString() ?: "null"} from ${characteristic.uuid}")
                    connectionCallback?.onCharacteristicRead(characteristic.uuid, value ?: byteArrayOf())
                }
            }
        }

        override fun onCharacteristicWrite(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) {
            handler.post {
                val value = characteristic.value
                addLog("Written ${value?.toHexString() ?: "null"} to ${characteristic.uuid}")
                value?.let { connectionCallback?.onCharacteristicWritten(characteristic.uuid, it) }
            }
        }

        override fun onCharacteristicChanged(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic) {
            handler.post {
                val value = characteristic.value
                addLog("Notification ${value?.toHexString() ?: "null"} from ${characteristic.uuid}")
                value?.let { connectionCallback?.onCharacteristicRead(characteristic.uuid, it) }
            }
        }
    }

    private fun ByteArray.toHexString(): String = joinToString("") { "%02X".format(it) }
}