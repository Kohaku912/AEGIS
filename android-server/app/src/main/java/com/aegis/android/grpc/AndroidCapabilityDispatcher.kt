package com.aegis.android.grpc

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.Settings
import androidx.core.content.ContextCompat
import aegis.AndroidServerOuterClass
import aegis.Common
import com.aegis.android.notification.AegisNotificationListener
import com.aegis.android.overlay.OverlayController
import com.aegis.android.provider.DeviceProvider
import com.aegis.android.provider.LocationProvider
import com.aegis.android.provider.ScreenshotProvider
import com.aegis.android.provider.UITreeProvider
import com.aegis.android.service.AegisAccessibilityService
import org.json.JSONArray
import org.json.JSONObject
import java.util.Base64

class AndroidCapabilityDispatcher(
    private val context: Context,
    private val overlayController: OverlayController,
    private val onApprovalDecision: (OverlayController.ApprovalAction) -> Unit,
) {
    companion object {
        private const val OK = 0
        private const val FAILED = 1

        val CAPABILITY_IDS = listOf(
            "android-server.device.get_status",
            "android-server.permissions.get_status",
            "android-server.accessibility.get_status",
            "android-server.overlay.show",
            "android-server.approval.request",
            "android-server.notification.get_notifications",
            "android-server.screen.get_current_app",
            "android-server.screen.get_ui_tree",
            "android-server.screen.get_screenshot",
            "android-server.ui.tap",
            "android-server.ui.swipe",
            "android-server.ui.type_text",
            "android-server.ui.back",
            "android-server.ui.home",
            "android-server.app.open",
            "android-server.location.get_current",
            "android-server.safety.emergency_stop",
        )
    }

    data class DispatchResult(
        val status: Common.Status,
        val resultJson: String,
    )

    private val deviceProvider = DeviceProvider(context)
    private val uiTreeProvider = UITreeProvider(context)
    private val screenshotProvider = ScreenshotProvider(context)
    private val locationProvider = LocationProvider(context)

    fun dispatch(command: AndroidServerOuterClass.AndroidInvokeCommand): DispatchResult {
        val params = parseParams(command.paramsJson)
        return when (command.capabilityId) {
            "android-server.device.get_status" -> deviceStatus()
            "android-server.permissions.get_status" -> permissionStatus()
            "android-server.accessibility.get_status" -> accessibilityStatus()
            "android-server.overlay.show" -> showOverlay(params)
            "android-server.approval.request" -> requestApproval(params)
            "android-server.notification.get_notifications" -> notifications(params)
            "android-server.screen.get_current_app" -> currentApp()
            "android-server.screen.get_ui_tree" -> uiTree()
            "android-server.screen.get_screenshot" -> screenshot()
            "android-server.ui.tap" -> tap(params)
            "android-server.ui.swipe" -> swipe(params)
            "android-server.ui.type_text" -> typeText(params)
            "android-server.ui.back" -> pressBack()
            "android-server.ui.home" -> pressHome()
            "android-server.app.open" -> openApp(params)
            "android-server.location.get_current" -> location()
            "android-server.safety.emergency_stop" -> emergencyStop(params)
            else -> error("UNREGISTERED_ANDROID_CAPABILITY", "Unknown Android capability: ${command.capabilityId}")
        }
    }

    fun permissionSnapshotJson(): JSONObject {
        val permissions = JSONArray()
        permissions.put(permission("notification_listener", AegisNotificationListener.isEnabled(context), "Notification listener access"))
        permissions.put(permission("accessibility", AegisAccessibilityService.instance != null, "AEGIS AccessibilityService"))
        permissions.put(permission("media_projection", screenshotProvider.isAvailable(), "MediaProjection screenshot consent"))
        permissions.put(permission("overlay", overlayController.canDrawOverlays(), "Draw over other apps"))
        permissions.put(permission("location", locationProvider.hasPermission(), "Fine or coarse location"))
        return JSONObject()
            .put("permissions", permissions)
            .put("screen_locked", deviceProvider.isLocked())
    }

    private fun deviceStatus(): DispatchResult {
        val device = deviceProvider.getDeviceInfo()
        return ok(
            JSONObject()
                .put("device_id", device.deviceId)
                .put("model", device.model)
                .put("manufacturer", device.manufacturer)
                .put("android_version", device.androidVersion)
                .put("sdk_version", device.sdkVersion)
                .put("battery_level", device.batteryLevel)
                .put("charging", device.batteryCharging)
                .put("screen_on", device.screenOn)
                .put("locked", device.locked)
                .put("wifi_connected", device.wifiConnected),
        )
    }

    private fun permissionStatus(): DispatchResult = ok(permissionSnapshotJson())

    private fun accessibilityStatus(): DispatchResult {
        val enabled = AegisAccessibilityService.instance != null
        return ok(
            JSONObject()
                .put("enabled", enabled)
                .put("service_name", "com.aegis.android.service.AegisAccessibilityService")
                .put("detail", if (enabled) "connected" else "disabled"),
        )
    }

    private fun showOverlay(params: JSONObject): DispatchResult {
        val shown = overlayController.showText(
            text = params.optString("text", params.optString("body", "AEGIS")),
            durationMs = params.optLong("duration_ms", 5000L),
        )
        return ok(JSONObject().put("shown", shown).put("surface_id", if (shown) "android_overlay" else "android_notification"))
    }

    private fun requestApproval(params: JSONObject): DispatchResult {
        val approvalId = params.optString("approval_id")
        if (approvalId.isBlank()) return error("INVALID_ARGUMENT", "approval_id is required")
        val shown = overlayController.showApproval(
            approvalId = approvalId,
            title = params.optString("title", "AEGIS approval"),
            body = params.optString("body", params.optString("summary_json", "")),
            onDecision = onApprovalDecision,
        )
        return ok(JSONObject().put("surface_id", if (shown) "android_overlay" else "android_notification").put("shown", shown))
    }

    private fun notifications(params: JSONObject): DispatchResult {
        if (!AegisNotificationListener.isEnabled(context)) {
            return error("ANDROID_PERMISSION_MISSING", "Notification listener is disabled")
        }
        val maxCount = params.optInt("max_count", 50).takeIf { it > 0 } ?: 50
        val items = JSONArray()
        AegisNotificationListener.recentNotifications(maxCount).forEach { item ->
            items.put(
                JSONObject()
                    .put("key", item.key)
                    .put("package_name", item.packageName)
                    .put("app_name", item.appName)
                    .put("title", item.title)
                    .put("text", item.text)
                    .put("posted_ms", item.postedMs)
                    .put("is_ongoing", item.isOngoing)
                    .put("is_clearable", item.isClearable),
            )
        }
        return ok(JSONObject().put("notifications", items))
    }

    private fun currentApp(): DispatchResult {
        if (!uiTreeProvider.isAvailable()) return error("ANDROID_PERMISSION_MISSING", "Accessibility service is disabled")
        val packageName = uiTreeProvider.currentPackageName()
        return ok(JSONObject().put("package_name", packageName).put("activity_name", "").put("app_name", appLabel(packageName)))
    }

    private fun uiTree(): DispatchResult {
        if (!uiTreeProvider.isAvailable()) return error("ANDROID_PERMISSION_MISSING", "Accessibility service is disabled")
        val root = uiTreeProvider.getUITree() ?: return error("ANDROID_COMMAND_FAILED", "UI tree is unavailable")
        return ok(JSONObject().put("root", nodeToJson(root)))
    }

    private fun screenshot(): DispatchResult {
        val result = screenshotProvider.captureScreenshot()
            ?: return error("ANDROID_PERMISSION_MISSING", "MediaProjection screenshot permission is missing")
        return ok(
            JSONObject()
                .put("image_base64", result.imageBase64)
                .put("width", result.width)
                .put("height", result.height)
                .put("format", result.format)
                .put("captured_at_ms", result.capturedAtMs),
        )
    }

    private fun tap(params: JSONObject): DispatchResult {
        if (!uiTreeProvider.isAvailable()) return error("ANDROID_PERMISSION_MISSING", "Accessibility service is disabled")
        val ok = uiTreeProvider.tapAt(params.optInt("x"), params.optInt("y"))
        return if (ok) ok(JSONObject().put("tapped", true)) else error("ANDROID_COMMAND_FAILED", "Tap failed")
    }

    private fun swipe(params: JSONObject): DispatchResult {
        if (!uiTreeProvider.isAvailable()) return error("ANDROID_PERMISSION_MISSING", "Accessibility service is disabled")
        val ok = uiTreeProvider.swipe(
            startX = params.optInt("start_x"),
            startY = params.optInt("start_y"),
            endX = params.optInt("end_x"),
            endY = params.optInt("end_y"),
            durationMs = params.optLong("duration_ms", 300L),
        )
        return if (ok) ok(JSONObject().put("swiped", true)) else error("ANDROID_COMMAND_FAILED", "Swipe failed")
    }

    private fun typeText(params: JSONObject): DispatchResult {
        if (!uiTreeProvider.isAvailable()) return error("ANDROID_PERMISSION_MISSING", "Accessibility service is disabled")
        val text = params.optString("text")
        if (text.isEmpty()) return error("INVALID_ARGUMENT", "text is required")
        val ok = uiTreeProvider.typeText(text)
        return if (ok) ok(JSONObject().put("characters_typed", text.length)) else error("ANDROID_COMMAND_FAILED", "Type text failed")
    }

    private fun pressBack(): DispatchResult {
        if (!uiTreeProvider.isAvailable()) return error("ANDROID_PERMISSION_MISSING", "Accessibility service is disabled")
        return if (uiTreeProvider.pressBack()) ok(JSONObject().put("pressed", "back")) else error("ANDROID_COMMAND_FAILED", "Back failed")
    }

    private fun pressHome(): DispatchResult {
        if (!uiTreeProvider.isAvailable()) return error("ANDROID_PERMISSION_MISSING", "Accessibility service is disabled")
        return if (uiTreeProvider.pressHome()) ok(JSONObject().put("pressed", "home")) else error("ANDROID_COMMAND_FAILED", "Home failed")
    }

    private fun openApp(params: JSONObject): DispatchResult {
        val packageName = params.optString("package_name")
        if (packageName.isBlank()) return error("INVALID_ARGUMENT", "package_name is required")
        val intent = context.packageManager.getLaunchIntentForPackage(packageName)
            ?: Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:$packageName"))
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        return try {
            context.startActivity(intent)
            ok(JSONObject().put("opened", true).put("package_name", packageName))
        } catch (exc: Exception) {
            error("ANDROID_COMMAND_FAILED", "Open app failed: ${exc.message}")
        }
    }

    private fun location(): DispatchResult {
        if (!locationProvider.hasPermission()) return error("ANDROID_PERMISSION_MISSING", "Location permission is missing")
        val location = locationProvider.getCurrentLocation()
            ?: return error("ANDROID_COMMAND_FAILED", "No location fix is available")
        return ok(
            JSONObject()
                .put("latitude", location.latitude)
                .put("longitude", location.longitude)
                .put("accuracy_meters", location.accuracyMeters.toDouble())
                .put("captured_ms", location.capturedMs),
        )
    }

    private fun emergencyStop(params: JSONObject): DispatchResult {
        overlayController.emergencyStop()
        return ok(JSONObject().put("stopped", true).put("reason", params.optString("reason", "")))
    }

    private fun permission(name: String, granted: Boolean, detail: String): JSONObject {
        return JSONObject().put("name", name).put("granted", granted).put("detail", detail)
    }

    private fun nodeToJson(node: UITreeProvider.UINode): JSONObject {
        val bounds = node.bounds
        val children = JSONArray()
        node.children.forEach { children.put(nodeToJson(it)) }
        return JSONObject()
            .put("class_name", node.className)
            .put("text", node.text)
            .put("content_desc", node.contentDescription)
            .put("resource_id", node.resourceId)
            .put("is_clickable", node.isClickable)
            .put("is_focusable", node.isFocusable)
            .put("is_password", node.isPassword)
            .put("x", bounds.getOrElse(0) { 0 })
            .put("y", bounds.getOrElse(1) { 0 })
            .put("width", bounds.getOrElse(2) { 0 } - bounds.getOrElse(0) { 0 })
            .put("height", bounds.getOrElse(3) { 0 } - bounds.getOrElse(1) { 0 })
            .put("children", children)
    }

    private fun appLabel(packageName: String): String {
        if (packageName.isBlank()) return ""
        return try {
            val info = context.packageManager.getApplicationInfo(packageName, 0)
            context.packageManager.getApplicationLabel(info).toString()
        } catch (_: Exception) {
            packageName.substringAfterLast('.')
        }
    }

    private fun ok(result: JSONObject): DispatchResult {
        return DispatchResult(status(OK, "ok"), result.toString())
    }

    private fun error(code: String, message: String): DispatchResult {
        val body = JSONObject().put("code", code).put("error", message)
        return DispatchResult(status(FAILED, "$code: $message"), body.toString())
    }

    private fun status(code: Int, message: String): Common.Status {
        return Common.Status.newBuilder().setCode(code).setMessage(message).build()
    }

    private fun parseParams(paramsJson: String): JSONObject {
        return try {
            if (paramsJson.isBlank()) JSONObject() else JSONObject(paramsJson)
        } catch (_: Exception) {
            JSONObject()
        }
    }
}
