package com.aegis.android

import android.Manifest
import android.app.Activity
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.text.InputType
import android.text.TextUtils
import android.text.method.PasswordTransformationMethod
import android.util.Log
import android.view.accessibility.AccessibilityManager
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.notification.AegisNotificationListener
import com.aegis.android.overlay.OverlayController
import com.aegis.android.provider.DeviceProvider
import com.aegis.android.provider.LocationProvider
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
        private const val REQUEST_LOCATION = 1002
        private const val REQUEST_NOTIFICATIONS = 1003
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private lateinit var grpcClient: AegisGrpcClient
    private lateinit var deviceProvider: DeviceProvider
    private lateinit var screenshotProvider: ScreenshotProvider
    private lateinit var uiTreeProvider: UITreeProvider
    private lateinit var locationProvider: LocationProvider
    private lateinit var overlayController: OverlayController

    private lateinit var statusText: TextView
    private lateinit var hostInput: EditText
    private lateinit var portInput: EditText
    private lateinit var tokenInput: EditText
    private lateinit var connectButton: Button
    private lateinit var notifAccessButton: Button
    private lateinit var screenshotButton: Button
    private lateinit var accessibilityButton: Button
    private lateinit var overlayButton: Button
    private lateinit var locationButton: Button
    private lateinit var notificationRuntimeButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        deviceProvider = DeviceProvider(this)
        screenshotProvider = ScreenshotProvider(this)
        uiTreeProvider = UITreeProvider(this)
        locationProvider = LocationProvider(this)
        overlayController = OverlayController(this)
        grpcClient = AegisGrpcClient.getInstance(this)

        val config = AegisConfig.load(this)
        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 40, 40, 40)
        }

        statusText = TextView(this).apply {
            textSize = 16f
            setPadding(0, 0, 0, 28)
        }
        content.addView(statusText)

        hostInput = EditText(this).apply {
            hint = "AEGIS Core host"
            setText(config.host)
            setSingleLine(true)
        }
        content.addView(hostInput)

        portInput = EditText(this).apply {
            hint = "AEGIS Core gRPC port"
            setText(config.port.toString())
            inputType = InputType.TYPE_CLASS_NUMBER
            setSingleLine(true)
        }
        content.addView(portInput)

        tokenInput = EditText(this).apply {
            hint = "Pairing token"
            setText(config.pairingToken)
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
            transformationMethod = PasswordTransformationMethod.getInstance()
            setSingleLine(true)
        }
        content.addView(tokenInput)

        notificationRuntimeButton = Button(this).apply {
            text = "Grant Android Notification Permission"
            setOnClickListener { requestRuntimeNotificationPermission() }
        }
        content.addView(notificationRuntimeButton)

        notifAccessButton = Button(this).apply {
            text = "Enable Notification Access"
            setOnClickListener { openNotificationAccessSettings() }
        }
        content.addView(notifAccessButton)

        accessibilityButton = Button(this).apply {
            text = "Enable Accessibility Service"
            setOnClickListener { openAccessibilitySettings() }
        }
        content.addView(accessibilityButton)

        screenshotButton = Button(this).apply {
            text = "Grant Screenshot Permission"
            setOnClickListener { requestScreenshotPermission() }
        }
        content.addView(screenshotButton)

        overlayButton = Button(this).apply {
            text = "Grant Overlay Permission"
            setOnClickListener { openOverlaySettings() }
        }
        content.addView(overlayButton)

        locationButton = Button(this).apply {
            text = "Grant Location Permission"
            setOnClickListener { requestLocationPermission() }
        }
        content.addView(locationButton)

        connectButton = Button(this).apply {
            text = "Connect Reverse Stream"
            setOnClickListener { connectToAegisCore() }
        }
        content.addView(connectButton)

        setContentView(ScrollView(this).apply { addView(content) })
        bindAccessibilityProvider()
        applyIntentConfig(intent)
        updateStatus()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        applyIntentConfig(intent)
        updateStatus()
    }

    override fun onResume() {
        super.onResume()
        bindAccessibilityProvider()
        grpcClient.pushPermissionChanged()
        updateStatus()
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_MEDIA_PROJECTION && resultCode == Activity.RESULT_OK && data != null) {
            screenshotProvider.setMediaProjectionResult(resultCode, data)
            Log.i(TAG, "Screenshot permission granted")
            grpcClient.pushPermissionChanged()
            updateStatus()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_LOCATION || requestCode == REQUEST_NOTIFICATIONS) {
            grpcClient.pushPermissionChanged()
            updateStatus()
        }
    }

    private fun updateStatus() {
        val notifEnabled = AegisNotificationListener.isEnabled(this)
        val connected = grpcClient.isConnected()
        val device = deviceProvider.getDeviceInfo()
        val accessibilityEnabled = isAccessibilityServiceEnabled()
        val screenshotAvailable = screenshotProvider.isAvailable()
        val overlayEnabled = overlayController.canDrawOverlays()
        val locationEnabled = locationProvider.hasPermission()
        val notificationRuntime = hasRuntimeNotificationPermission()

        statusText.text = buildString {
            appendLine("AEGIS Android Server v0.2.0")
            appendLine("Device ID: ${AegisConfig.load(this@MainActivity).deviceId}")
            appendLine()
            appendLine("AEGIS Core: ${if (connected) "Connected" else "Disconnected"}")
            appendLine("Last heartbeat: ${grpcClient.lastHeartbeatMs().takeIf { it > 0 } ?: "-"}")
            appendLine()
            appendLine("Notification runtime: ${if (notificationRuntime) "Granted" else "Missing"}")
            appendLine("Notification access: ${if (notifEnabled) "Enabled" else "Disabled"}")
            appendLine("Accessibility: ${if (accessibilityEnabled) "Enabled" else "Disabled"}")
            appendLine("Screenshot: ${if (screenshotAvailable) "Granted" else "Not granted"}")
            appendLine("Overlay: ${if (overlayEnabled) "Granted" else "Missing"}")
            appendLine("Location: ${if (locationEnabled) "Granted" else "Missing"}")
            appendLine()
            appendLine("Device: ${device.manufacturer} ${device.model}")
            appendLine("Android: ${device.androidVersion} (SDK ${device.sdkVersion})")
            appendLine("Battery: ${device.batteryLevel}%${if (device.batteryCharging) " charging" else ""}")
            appendLine("Screen: ${if (device.screenOn) "On" else "Off"} / ${if (device.locked) "Locked" else "Unlocked"}")
        }

        notificationRuntimeButton.isEnabled = !notificationRuntime
        notifAccessButton.isEnabled = !notifEnabled
        accessibilityButton.isEnabled = !accessibilityEnabled
        screenshotButton.isEnabled = !screenshotAvailable
        overlayButton.isEnabled = !overlayEnabled
        locationButton.isEnabled = !locationEnabled
        connectButton.isEnabled = !connected
    }

    private fun bindAccessibilityProvider() {
        AegisAccessibilityService.instance?.let { uiTreeProvider.setAccessibilityService(it) }
    }

    private fun hasRuntimeNotificationPermission(): Boolean {
        return Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val enabledServices = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES)
        if (TextUtils.isEmpty(enabledServices)) return false
        val myComponent = ComponentName(this, AegisAccessibilityService::class.java).flattenToString()
        return enabledServices?.split(":")?.any { it == myComponent } == true
    }

    private fun openNotificationAccessSettings() {
        startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
    }

    private fun openAccessibilitySettings() {
        startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
    }

    private fun openOverlaySettings() {
        startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName")))
    }

    private fun requestRuntimeNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), REQUEST_NOTIFICATIONS)
        }
    }

    private fun requestLocationPermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION),
            REQUEST_LOCATION,
        )
    }

    private fun requestScreenshotPermission() {
        val serviceIntent = Intent(this, ScreenshotService::class.java)
        startForegroundService(serviceIntent)
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        startActivityForResult(projectionManager.createScreenCaptureIntent(), REQUEST_MEDIA_PROJECTION)
    }

    private fun connectToAegisCore() {
        val host = hostInput.text.toString()
        val port = portInput.text.toString().toIntOrNull() ?: 50051
        val token = tokenInput.text.toString()
        AegisConfig.save(this, host, port, token)
        grpcClient = AegisGrpcClient.getInstance(this)
        startForegroundService(Intent(this, AegisForegroundService::class.java))
        scope.launch {
            statusText.text = "Connecting to AEGIS Core..."
            connectButton.isEnabled = false
            try {
                val success = grpcClient.connect()
                statusText.text = if (success) "Connected to AEGIS Core reverse stream." else "Failed to connect. Check host, port, and pairing token."
            } catch (e: Exception) {
                Log.e(TAG, "Connection error", e)
                statusText.text = "Connection error: ${e.message}"
            }
            updateStatus()
        }
    }

    private fun applyIntentConfig(intent: Intent?) {
        intent ?: return
        val host = intent.getStringExtra("host")
        val token = intent.getStringExtra("pairing_token")
        val port = if (intent.hasExtra("port")) intent.getIntExtra("port", 50051) else null
        if (host != null || token != null || port != null) {
            val current = AegisConfig.load(this)
            val next = AegisConfig.save(
                this,
                host ?: current.host,
                port ?: current.port,
                token ?: current.pairingToken,
            )
            hostInput.setText(next.host)
            portInput.setText(next.port.toString())
            tokenInput.setText(next.pairingToken)
            grpcClient = AegisGrpcClient.getInstance(this)
        }
        if (intent.getBooleanExtra("auto_connect", false) && !grpcClient.isConnected()) {
            connectToAegisCore()
        }
    }
}
