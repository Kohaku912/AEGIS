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
        @Volatile private var screenTitleSummary: String = ""
        @Volatile private var screenTitleHash: String = ""
        @Volatile private var contentKind: String = "unknown"
        @Volatile private var inputTargetCategory: String = "none"

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
            contentKind = contentKindFor(semanticCategory)
            inputTargetCategory = inputTargetCategoryFor(event, semanticCategory)
            val safeTitle = safeScreenTitle(event, semanticCategory)
            if (safeTitle.isNotBlank()) {
                screenTitleSummary = safeTitle
                screenTitleHash = sha256(safeTitle)
            }
            layoutHash = sha256("${event.className}:${event.eventType}:$packageName:$semanticCategory:$screenTitleHash")
        }

        fun recordScreenDetail(packageName: String, summary: String, category: String) {
            val safeSummary = sanitizeScreenSummary(summary)
            if (packageName.isNotBlank()) foregroundPackage = packageName
            if (safeSummary.isBlank()) return
            semanticCategory = category
            contentKind = contentKindFor(category)
            inputTargetCategory = "none"
            screenTitleSummary = safeSummary
            screenTitleHash = sha256(safeSummary)
            layoutHash = sha256("$packageName:$category:$screenTitleHash")
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

        private fun contentKindFor(category: String): String = when (category) {
            "video" -> "video"
            "browser" -> "browser"
            "chat" -> "chat"
            "inputting" -> "input"
            "login" -> "login"
            else -> category
        }

        private fun inputTargetCategoryFor(event: AccessibilityEvent, category: String): String {
            val cls = event.className?.toString().orEmpty().lowercase()
            return when {
                event.isPassword -> "password"
                "edittext" in cls -> category
                category in setOf("login", "inputting") -> category
                else -> "none"
            }
        }

        private fun safeScreenTitle(event: AccessibilityEvent, category: String): String {
            if (event.isPassword || category in setOf("login", "inputting", "chat")) return ""
            if (category !in setOf("video", "browser", "home", "settings")) return ""
            val raw = event.text?.joinToString(" ")?.trim().orEmpty()
                .ifBlank { event.contentDescription?.toString()?.trim().orEmpty() }
            return sanitizeScreenSummary(raw)
        }

        private fun sanitizeScreenSummary(raw: String): String {
            val cleaned = raw
                .replace(Regex("\\b\\d{6,}\\b"), "<code>")
                .replace(Regex("(?i)(password|passcode|otp|verification code|token|secret|認証コード).*"), "<redacted>")
                .trim()
            if (cleaned.isBlank() || cleaned == "<redacted>") return ""
            return cleaned.take(120)
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
            .put("package_name", foregroundPackage.ifBlank { AegisAccessibilityService.lastForegroundPackage() })
            .put("app_name", appName(foregroundPackage.ifBlank { AegisAccessibilityService.lastForegroundPackage() }))
            .put("touch_count", touchCounter.getAndSet(0))
            .put("layout_category", semanticCategory)
            .put("semantic_summary", listOf(semanticCategory, screenTitleSummary).filter { it.isNotBlank() }.joinToString(": "))
            .put("screen_title_summary", screenTitleSummary)
            .put("screen_title_hash", screenTitleHash)
            .put("content_kind", contentKind)
            .put("input_target_category", inputTargetCategory)
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

    private fun appName(packageName: String): String {
        if (packageName.isBlank()) return ""
        return runCatching {
            val pm = context.packageManager
            val info = pm.getApplicationInfo(packageName, 0)
            pm.getApplicationLabel(info).toString().takeUnless { it.isBlank() || it == packageName }
                ?: fallbackAppName(packageName)
        }.getOrElse { fallbackAppName(packageName) }
    }

    private fun fallbackAppName(packageName: String): String = when (packageName) {
        "com.google.android.youtube" -> "YouTube"
        "com.android.chrome" -> "Chrome"
        "com.google.android.googlequicksearchbox" -> "Google"
        "com.android.systemui" -> "System UI"
        else -> packageName
    }
}
