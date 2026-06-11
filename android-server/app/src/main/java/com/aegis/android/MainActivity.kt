package com.aegis.android

import android.content.ComponentName
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.text.TextUtils
import android.util.Log
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.provider.DeviceProvider
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

/**
 * Main activity for AEGIS Android Server.
 *
 * Shows connection status and provides button to enable notification access.
 */
class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "AegisMainActivity"
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private lateinit var grpcClient: AegisGrpcClient
    private lateinit var deviceProvider: DeviceProvider

    private lateinit var statusText: TextView
    private lateinit var connectButton: Button
    private lateinit var notifAccessButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Simple layout programmatically (no XML dependency)
        val layout = android.widget.LinearLayout(this).apply {
            orientation = android.widget.LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
        }

        statusText = TextView(this).apply {
            text = "AEGIS Android Server v0.1.0"
            textSize = 20f
            setPadding(0, 0, 0, 32)
        }
        layout.addView(statusText)

        notifAccessButton = Button(this).apply {
            text = "Enable Notification Access"
            setOnClickListener { openNotificationAccessSettings() }
        }
        layout.addView(notifAccessButton)

        connectButton = Button(this).apply {
            text = "Connect to AEGIS Core"
            setOnClickListener { connectToAegisCore() }
        }
        layout.addView(connectButton)

        setContentView(layout)

        grpcClient = AegisGrpcClient.getInstance()
        deviceProvider = DeviceProvider(this)

        updateStatus()
    }

    override fun onResume() {
        super.onResume()
        updateStatus()
    }

    private fun updateStatus() {
        val notifEnabled = isNotificationListenerEnabled()
        val connected = grpcClient.isConnected()
        val device = deviceProvider.getDeviceInfo()

        statusText.text = buildString {
            appendLine("AEGIS Android Server v0.1.0")
            appendLine()
            appendLine("Notification Access: ${if (notifEnabled) "✓ Enabled" else "✗ Disabled"}")
            appendLine("AEGIS Core: ${if (connected) "✓ Connected" else "✗ Disconnected"}")
            appendLine()
            appendLine("Device: ${device.manufacturer} ${device.model}")
            appendLine("Android: ${device.androidVersion} (SDK ${device.sdkVersion})")
            appendLine("Battery: ${device.batteryLevel}%${if (device.batteryCharging) " (Charging)" else ""}")
            appendLine("Screen: ${if (device.screenOn) "On" else "Off"}")
            appendLine("WiFi: ${if (device.wifiConnected) "Connected" else "Disconnected"}")
        }

        notifAccessButton.isEnabled = !notifEnabled
        connectButton.isEnabled = !connected
    }

    private fun isNotificationListenerEnabled(): Boolean {
        val flat = Settings.Secure.getString(contentResolver, "enabled_notification_listeners")
        if (TextUtils.isEmpty(flat)) return false
        val myComponent = ComponentName(this, AegisNotificationListener::class.java).flattenToString()
        return flat.split(":").any { it == myComponent }
    }

    private fun openNotificationAccessSettings() {
        try {
            startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
        } catch (e: Exception) {
            Log.e(TAG, "Failed to open notification settings", e)
        }
    }

    private fun connectToAegisCore() {
        scope.launch {
            statusText.text = "Connecting to AEGIS Core..."
            val success = grpcClient.connect()
            if (success) {
                grpcClient.registerCapabilities()
                // Start foreground service for persistent connection
                val serviceIntent = Intent(this@MainActivity, AegisForegroundService::class.java)
                startForegroundService(serviceIntent)
            }
            updateStatus()
        }
    }
}
