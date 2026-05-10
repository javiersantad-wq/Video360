package com.cfmoto.blescanner

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.cfmoto.blescanner.BleScanner.BleDevice

class DeviceAdapter(private val devices: List<BleDevice>, private val onConnectClick: (BleDevice) -> Unit) : RecyclerView.Adapter<DeviceAdapter.DeviceViewHolder>() {
    class DeviceViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvDeviceName: TextView = itemView.findViewById(R.id.tv_device_name)
        val tvDeviceAddress: TextView = itemView.findViewById(R.id.tv_device_address)
        val tvServices: TextView = itemView.findViewById(R.id.tv_services)
        val tvRssi: TextView = itemView.findViewById(R.id.tv_rssi)
        val tvCfMotoTag: TextView = itemView.findViewById(R.id.tv_cfmoto_tag)
        val signalIndicator: View = itemView.findViewById(R.id.signal_indicator)
        val btnConnect: Button = itemView.findViewById(R.id.btn_connect)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): DeviceViewHolder = DeviceViewHolder(LayoutInflater.from(parent.context).inflate(R.layout.item_device, parent, false))

    override fun onBindViewHolder(holder: DeviceViewHolder, position: Int) {
        val device = devices[position]
        val context = holder.itemView.context
        holder.tvDeviceName.text = device.name ?: "Unknown"
        holder.tvDeviceAddress.text = device.address
        holder.tvRssi.text = "${device.rssi} dBm"
        holder.tvServices.text = "Services: ${if (device.serviceUuids.isNotEmpty()) device.serviceUuids.take(2).joinToString(", ") { it.toString().takeLast(4) } else "None"}"
        val signalColor = when { device.rssi >= -60 -> ContextCompat.getColor(context, R.color.signalExcellent); device.rssi >= -75 -> ContextCompat.getColor(context, R.color.signalGood); device.rssi >= -90 -> ContextCompat.getColor(context, R.color.signalMedium); else -> ContextCompat.getColor(context, R.color.signalWeak) }
        holder.signalIndicator.setBackgroundColor(signalColor)
        holder.tvRssi.setTextColor(signalColor)
        holder.tvCfMotoTag.visibility = if (device.isCfMoto) View.VISIBLE else View.GONE
        holder.btnConnect.setOnClickListener { onConnectClick(device) }
    }

    override fun getItemCount(): Int = devices.size
}