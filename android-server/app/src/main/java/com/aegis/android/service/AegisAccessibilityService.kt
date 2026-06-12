package com.aegis.android.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import com.aegis.android.provider.UITreeProvider

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
        var instance: AegisAccessibilityService? = null
            private set
        var uiTreeProvider: UITreeProvider? = null
            private set
    }

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
        // We don't need to process events in real-time
        // The UITreeProvider will query the tree on demand
    }

    override fun onInterrupt() {
        Log.w(TAG, "AccessibilityService interrupted")
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        Log.i(TAG, "AccessibilityService destroyed")
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
