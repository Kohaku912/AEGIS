package com.aegis.android.provider

import android.content.Context
import android.net.wifi.WifiManager
import android.view.accessibility.AccessibilityEvent
import com.aegis.android.service.AegisAccessibilityService
import org.json.JSONObject
import java.security.MessageDigest
import java.util.concurrent.atomic.AtomicInteger

class UserActivityCollector(private val context: Context) {
    companion object {
        private val touchCounter = AtomicInteger(0)
        @Volatile private var foregroundPackage: String = ""
        @Volatile private var semanticCategory: String = "unknown"
        @Volatile private var layoutHash: String = ""

        fun recordAccessibilityEvent(event: AccessibilityEvent) {
            val packageName = event.packageName?.toString().orEmpty()
            if (packageName.isNotBlank()) foregroundPackage = packageName
            when (event.eventType) {
                AccessibilityEvent.TYPE_VIEW_CLICKED,
                AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED,
                AccessibilityEvent.TYPE_VIEW_FOCUSED,
                AccessibilityEvent.TYPE_TOUCH_INTERACTION_END -> touchCounter.incrementAndGet()
            }
            semanticCategory = classifyEvent(event)
            layoutHash = sha256("${event.className}:${event.eventType}:$packageName")
        }

        private fun classifyEvent(event: AccessibilityEvent): String {
            val cls = event.className?.toString().orEmpty().lowercase()
            val pkg = event.packageName?.toString().orEmpty().lowercase()
            return when {
                event.isPassword -> "login"
                "edittext" in cls -> "inputting"
                "youtube" in pkg || "video" in pkg -> "video"
                "browser" in pkg || "chrome" in pkg || "firefox" in pkg || "edge" in pkg -> "browser"
                "launcher" in pkg -> "home"
                "settings" in pkg -> "settings"
                "discord" in pkg || "line" in pkg || "slack" in pkg || "message" in pkg -> "chat"
                else -> "unknown"
            }
        }

        private fun sha256(value: String): String {
            val digest = MessageDigest.getInstance("SHA-256").digest(value.toByteArray(Charsets.UTF_8))
            return digest.joinToString("") { "%02x".format(it) }
        }
    }

    private val deviceProvider = DeviceProvider(context)
    private val locationProvider = LocationProvider(context)
    private var lastPayloadHash = ""

    fun collectIfChanged(): JSONObject? {
        val payload = collect()
        val hash = sha256(payload.toString())
        if (hash == lastPayloadHash) return null
        lastPayloadHash = hash
        return payload
    }

    fun collect(): JSONObject {
        val device = deviceProvider.getDeviceInfo()
        val wifi = wifiInfo()
        val location = locationProvider.getCurrentLocation()
        val payload = JSONObject()
            .put("event_type", "android.user_activity.changed")
            .put("timestamp_ms", System.currentTimeMillis())
            .put("screen_on", device.screenOn)
            .put("locked", device.locked)
            .put("wifi_connected", device.wifiConnected)
            .put("foreground_app", foregroundPackage.ifBlank { AegisAccessibilityService.lastForegroundPackage() })
            .put("touch_count", touchCounter.getAndSet(0))
            .put("layout_category", semanticCategory)
            .put("semantic_summary", semanticCategory)
            .put("layout_hash", layoutHash)
        wifi?.let {
            payload.put("wifi_ssid", it.first)
            payload.put("wifi_bssid", it.second)
        }
        location?.let {
            payload.put("gps_available", true)
            payload.put("latitude_bucket", kotlin.math.round(it.latitude * 100.0) / 100.0)
            payload.put("longitude_bucket", kotlin.math.round(it.longitude * 100.0) / 100.0)
            payload.put("location_accuracy_m", it.accuracyMeters)
            payload.put("location_captured_ms", it.capturedMs)
        }
        return payload
    }

    @Suppress("DEPRECATION")
    private fun wifiInfo(): Pair<String, String>? {
        return runCatching {
            val manager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
            val info = manager.connectionInfo ?: return null
            val ssid = info.ssid?.trim('"').orEmpty()
            val bssid = info.bssid.orEmpty()
            if (ssid.isBlank() && bssid.isBlank()) null else ssid to bssid
        }.getOrNull()
    }
}
