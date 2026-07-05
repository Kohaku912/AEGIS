package com.aegis.android.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.provider.UITreeProvider
import com.aegis.android.provider.UserActivityCollector

/**
 * AccessibilityService for AEGIS Android.
 *
 * Provides:
 * - UI tree extraction
 * - Tap/swipe gestures
 * - Text input
 *
 * User must enable this in Settings > Accessibility > AEGIS Android
 */
class AegisAccessibilityService : AccessibilityService() {

    companion object {
        private const val TAG = "AegisAccessibility"
        private const val ACTIVITY_PUSH_THROTTLE_MS = 5_000L
        var instance: AegisAccessibilityService? = null
            private set
        var uiTreeProvider: UITreeProvider? = null
            private set
        private var lastForegroundPackage: String = ""

        fun lastForegroundPackage(): String = lastForegroundPackage
    }

    private val userActivityCollector by lazy { UserActivityCollector(this) }
    private var lastActivityPushMs: Long = 0L

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this

        // Configure the service
        val info = serviceInfo.apply {
            eventTypes = AccessibilityEvent.TYPES_ALL_MASK
            feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC
            flags = AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS or
                    AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS or
                    AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
            notificationTimeout = 100
        }
        serviceInfo = info

        Log.i(TAG, "AccessibilityService connected")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        val packageName = event?.packageName?.toString() ?: return
        UserActivityCollector.recordAccessibilityEvent(event)
        val category = screenCategory(packageName)
        if (category in setOf("video", "browser")) {
            extractSafeScreenSummary(category)?.let { summary ->
                UserActivityCollector.recordScreenDetail(packageName, summary, category)
            }
        }
        if (event.eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED && packageName != lastForegroundPackage) {
            lastForegroundPackage = packageName
            AegisGrpcClient.current()?.pushForegroundApp(packageName)
        }
        if (shouldPushActivity(event)) {
            lastActivityPushMs = System.currentTimeMillis()
            AegisGrpcClient.current()?.pushUserActivity(userActivityCollector.collect().toString())
        }
    }

    override fun onInterrupt() {
        Log.w(TAG, "AccessibilityService interrupted")
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        Log.i(TAG, "AccessibilityService destroyed")
    }

    private fun shouldPushActivity(event: AccessibilityEvent): Boolean {
        val now = System.currentTimeMillis()
        if (now - lastActivityPushMs < ACTIVITY_PUSH_THROTTLE_MS) return false
        return when (event.eventType) {
            AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED,
            AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED,
            AccessibilityEvent.TYPE_VIEW_CLICKED,
            AccessibilityEvent.TYPE_TOUCH_INTERACTION_END -> true
            else -> false
        }
    }

    private fun screenCategory(packageName: String): String {
        val pkg = packageName.lowercase()
        return when {
            "youtube" in pkg || "video" in pkg -> "video"
            "browser" in pkg || "chrome" in pkg || "firefox" in pkg || "edge" in pkg -> "browser"
            else -> "unknown"
        }
    }

    private fun extractSafeScreenSummary(category: String): String? {
        val root = rootInActiveWindow ?: return null
        val candidates = mutableListOf<String>()
        collectSafeTextCandidates(root, candidates, max = 180)
        return candidates
            .map { it.trim() }
            .filter { isUsefulScreenSummary(it, category) }
            .maxByOrNull { scoreScreenSummary(it, category) }
            ?.take(120)
    }

    private fun collectSafeTextCandidates(
        node: android.view.accessibility.AccessibilityNodeInfo,
        out: MutableList<String>,
        max: Int,
    ) {
        if (out.size >= max) return
        if (!node.isPassword) {
            val text = node.text?.toString().orEmpty()
            val desc = node.contentDescription?.toString().orEmpty()
            if (text.isNotBlank()) out.add(text)
            if (desc.isNotBlank()) out.add(desc)
        }
        for (i in 0 until node.childCount) {
            if (out.size >= max) return
            val child = node.getChild(i) ?: continue
            try {
                collectSafeTextCandidates(child, out, max)
            } finally {
                child.recycle()
            }
        }
    }

    private fun isUsefulScreenSummary(value: String, category: String): Boolean {
        if (value.length < 4 || value.length > 120) return false
        if (Regex("\\b\\d{6,}\\b").containsMatchIn(value)) return false
        if (Regex("(?i)(password|passcode|otp|verification|token|secret)").containsMatchIn(value)) return false
        val lower = value.lowercase()
        if (category == "video" && lower.contains("launcher")) return false
        val commonControls = setOf(
            "youtube", "home", "shorts", "subscriptions", "library", "search", "share",
            "comments", "settings", "more", "back", "pause", "play", "like",
            "ホーム", "ショート", "登録チャンネル", "マイページ", "検索", "共有", "コメント", "その他", "戻る",
        )
        if (commonControls.any { lower == it.lowercase() || lower.contains(it.lowercase()) && value.length < 16 }) {
            return false
        }
        if (category == "video" && Regex("^[\\d\\s:.,万万人件]+$").matches(value)) return false
        return true
    }

    private fun scoreScreenSummary(value: String, category: String): Int {
        var score = value.length.coerceAtMost(80)
        if (category == "video" && Regex("[。.!?！？]").containsMatchIn(value)) score += 20
        if (category == "browser" && Regex("[-|｜]").containsMatchIn(value)) score += 10
        if (Regex("(?i)(comment|share|subscribe|チャンネル登録|高く評価)").containsMatchIn(value)) score -= 30
        return score
    }

    /**
     * Get the current UI tree.
     */
    fun getUITree(): UITreeProvider.UINode? {
        val rootNode = rootInActiveWindow ?: return null
        return buildUINode(rootNode)
    }

    private fun buildUINode(node: android.view.accessibility.AccessibilityNodeInfo): UITreeProvider.UINode {
        val bounds = android.graphics.Rect()
        node.getBoundsInScreen(bounds)

        val children = mutableListOf<UITreeProvider.UINode>()
        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                children.add(buildUINode(child))
                child.recycle()
            }
        }

        return UITreeProvider.UINode(
            className = node.className?.toString() ?: "",
            text = node.text?.toString() ?: "",
            contentDescription = node.contentDescription?.toString() ?: "",
            resourceId = node.viewIdResourceName ?: "",
            isClickable = node.isClickable,
            isFocusable = node.isFocusable,
            isPassword = node.isPassword,
            bounds = listOf(bounds.left, bounds.top, bounds.right, bounds.bottom),
            children = children
        )
    }
}
