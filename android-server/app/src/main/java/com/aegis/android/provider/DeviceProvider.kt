package com.aegis.android.provider

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Build
import android.os.PowerManager
import android.util.Log

/**
 * Provides device state information (battery, screen, connectivity).
 */
class DeviceProvider(private val context: Context) {

    companion object {
        private const val TAG = "DeviceProvider"
    }

    data class DeviceInfo(
        val model: String,
        val manufacturer: String,
        val androidVersion: String,
        val sdkVersion: Int,
        val batteryLevel: Int,
        val batteryCharging: Boolean,
        val screenOn: Boolean,
        val wifiConnected: Boolean,
    )

    data class BatteryInfo(
        val level: Int,
        val isCharging: Boolean,
    )

    /**
     * Get comprehensive device information.
     */
    fun getDeviceInfo(): DeviceInfo {
        val battery = getBatteryInfo()
        return DeviceInfo(
            model = Build.MODEL,
            manufacturer = Build.MANUFACTURER,
            androidVersion = Build.VERSION.RELEASE,
            sdkVersion = Build.VERSION.SDK_INT,
            batteryLevel = battery.level,
            batteryCharging = battery.isCharging,
            screenOn = isScreenOn(),
            wifiConnected = isWifiConnected(),
        )
    }

    /**
     * Get battery level and charging status.
     */
    fun getBatteryInfo(): BatteryInfo {
        val batteryIntent = context.registerReceiver(
            null,
            IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        )

        val level = batteryIntent?.let {
            val current = it.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            val total = it.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            if (current >= 0 && total > 0) (current * 100 / total) else 0
        } ?: 0

        val status = batteryIntent?.getIntExtra(
            BatteryManager.EXTRA_STATUS, -1
        ) ?: -1
        val isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING ||
                status == BatteryManager.BATTERY_STATUS_FULL

        return BatteryInfo(level = level, isCharging = isCharging)
    }

    /**
     * Check if the screen is currently on.
     */
    fun isScreenOn(): Boolean {
        val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
        return powerManager.isInteractive
    }

    /**
     * Check if connected to WiFi.
     */
    fun isWifiConnected(): Boolean {
        val connectivityManager = context.getSystemService(
            Context.CONNECTIVITY_SERVICE
        ) as ConnectivityManager

        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false

        return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
    }
}
