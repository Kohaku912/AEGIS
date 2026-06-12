package com.aegis.android

import android.accessibilityservice.AccessibilityServiceInfo
import android.app.Activity
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.os.Bundle
import android.provider.Settings
import android.text.TextUtils
import android.util.Log
import android.view.accessibility.AccessibilityManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.notification.AegisNotificationListener
import com.aegis.android.provider.DeviceProvider
import com.aegis.android.provider.ScreenshotProvider
import com.aegis.android.provider.UITreeProvider
import com.aegis.android.service.AegisAccessibilityService
import com.aegis.android.service.ScreenshotService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "AegisMainActivity"
        private const val REQUEST_MEDIA_PROJECTION = 1001
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private lateinit var grpcClient: AegisGrpcClient
    private lateinit var deviceProvider: DeviceProvider
    private lateinit var screenshotProvider: ScreenshotProvider
    private lateinit var uiTreeProvider: UITreeProvider

    private lateinit var statusText: TextView
    private lateinit var connectButton: Button
    private lateinit var notifAccessButton: Button
    private lateinit var screenshotButton: Button
    private lateinit var accessibilityButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
        }

        statusText = TextView(this).apply {
            text = "AEGIS Android Server v0.2.0"
            textSize = 18f
            setPadding(0, 0, 0, 32)
        }
        layout.addView(statusText)

        notifAccessButton = Button(this).apply {
            text = "Enable Notification Access"
            setOnClickListener { openNotificationAccessSettings() }
        }
        layout.addView(notifAccessButton)

        accessibilityButton = Button(this).apply {
            text = "Enable Accessibility Service"
            setOnClickListener { openAccessibilitySettings() }
        }
        layout.addView(accessibilityButton)

        screenshotButton = Button(this).apply {
            text = "Grant Screenshot Permission"
            setOnClickListener { requestScreenshotPermission() }
        }
        layout.addView(screenshotButton)

        connectButton = Button(this).apply {
            text = "Connect to AEGIS Core"
            setOnClickListener { connectToAegisCore() }
        }
        layout.addView(connectButton)

        setContentView(layout)

        grpcClient = AegisGrpcClient.getInstance("192.168.50.175", 50051)
        deviceProvider = DeviceProvider(this)
        screenshotProvider = ScreenshotProvider(this)
        uiTreeProvider = UITreeProvider(this)

        // Check if AccessibilityService is already connected
        if (AegisAccessibilityService.instance != null) {
            uiTreeProvider.setAccessibilityService(AegisAccessibilityService.instance!!)
        }

        updateStatus()
    }

    override fun onResume() {
        super.onResume()
        // Check if AccessibilityService was enabled
        if (AegisAccessibilityService.instance != null && !uiTreeProvider.isAvailable()) {
            uiTreeProvider.setAccessibilityService(AegisAccessibilityService.instance!!)
        }
        updateStatus()
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_MEDIA_PROJECTION && resultCode == Activity.RESULT_OK && data != null) {
            screenshotProvider.setMediaProjectionResult(resultCode, data)
            Log.i(TAG, "Screenshot permission granted")
            updateStatus()
        }
    }

    private fun updateStatus() {
        val notifEnabled = isNotificationListenerEnabled()
        val connected = grpcClient.isConnected()
        val device = deviceProvider.getDeviceInfo()
        val accessibilityEnabled = isAccessibilityServiceEnabled()
        val screenshotAvailable = screenshotProvider.isAvailable()

        statusText.text = buildString {
            appendLine("AEGIS Android Server v0.2.0")
            appendLine()
            appendLine("Notification Access: ${if (notifEnabled) "✓ Enabled" else "✗ Disabled"}")
            appendLine("Accessibility Service: ${if (accessibilityEnabled) "✓ Enabled" else "✗ Disabled"}")
            appendLine("Screenshot Permission: ${if (screenshotAvailable) "✓ Granted" else "✗ Not Granted"}")
            appendLine("AEGIS Core: ${if (connected) "✓ Connected" else "✗ Disconnected"}")
            appendLine()
            appendLine("Device: ${device.manufacturer} ${device.model}")
            appendLine("Android: ${device.androidVersion} (SDK ${device.sdkVersion})")
            appendLine("Battery: ${device.batteryLevel}%${if (device.batteryCharging) " (Charging)" else ""}")
            appendLine("Screen: ${if (device.screenOn) "On" else "Off"}")
        }

        notifAccessButton.isEnabled = !notifEnabled
        accessibilityButton.isEnabled = !accessibilityEnabled
        screenshotButton.isEnabled = !screenshotAvailable
        connectButton.isEnabled = !connected
    }

    private fun isNotificationListenerEnabled(): Boolean {
        val flat = Settings.Secure.getString(contentResolver, "enabled_notification_listeners")
        if (TextUtils.isEmpty(flat)) return false
        val myComponent = ComponentName(this, AegisNotificationListener::class.java).flattenToString()
        return flat.split(":").any { it == myComponent }
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val am = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        val enabledServices = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES)
        if (TextUtils.isEmpty(enabledServices)) return false
        val myComponent = ComponentName(this, AegisAccessibilityService::class.java).flattenToString()
        return enabledServices?.split(":")?.any { it == myComponent } == true
    }

    private fun openNotificationAccessSettings() {
        try {
            startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
        } catch (e: Exception) {
            Log.e(TAG, "Failed to open notification settings", e)
        }
    }

    private fun openAccessibilitySettings() {
        try {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        } catch (e: Exception) {
            Log.e(TAG, "Failed to open accessibility settings", e)
        }
    }

    private fun requestScreenshotPermission() {
        try {
            // Start foreground service first (required for MediaProjection)
            val serviceIntent = Intent(this, ScreenshotService::class.java)
            startForegroundService(serviceIntent)

            // Then request MediaProjection permission
            val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
            startActivityForResult(projectionManager.createScreenCaptureIntent(), REQUEST_MEDIA_PROJECTION)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to request screenshot permission", e)
        }
    }

    private fun connectToAegisCore() {
        scope.launch {
            statusText.text = "Connecting to AEGIS Core..."
            connectButton.isEnabled = false
            try {
                val success = grpcClient.connect()
                if (success) {
                    grpcClient.registerCapabilities()
                    statusText.text = "Connected to AEGIS Core!"
                } else {
                    statusText.text = "Failed to connect to AEGIS Core"
                }
            } catch (e: Exception) {
                Log.e(TAG, "Connection error", e)
                statusText.text = "Connection error: ${e.message}"
            }
            updateStatus()
        }
    }
}
