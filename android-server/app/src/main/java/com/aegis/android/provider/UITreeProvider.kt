package com.aegis.android.provider

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.content.Context
import android.content.Intent
import android.graphics.Rect
import android.os.Build
import android.util.Log
import android.view.accessibility.AccessibilityNodeInfo

/**
 * UI Tree provider using AccessibilityService.
 *
 * Provides:
 * - UI tree extraction
 * - Tap at coordinates
 * - Swipe gestures
 * - Text input
 *
 * Requires user to enable AccessibilityService in Settings.
 */
class UITreeProvider(private val context: Context) {

    companion object {
        private const val TAG = "UITreeProvider"
    }

    private var accessibilityService: AccessibilityService? = null

    /**
     * Set the AccessibilityService instance.
     * Called from the service's onServiceConnected.
     */
    fun setAccessibilityService(service: AccessibilityService) {
        accessibilityService = service
        Log.i(TAG, "AccessibilityService connected")
    }

    /**
     * Check if AccessibilityService is available.
     */
    fun isAvailable(): Boolean {
        return accessibilityService != null
    }

    /**
     * Get the UI tree from the current screen.
     */
    fun getUITree(): UINode? {
        val service = accessibilityService ?: run {
            Log.w(TAG, "AccessibilityService not available")
            return null
        }

        try {
            val rootNode = service.rootInActiveWindow ?: return null
            return buildUINode(rootNode)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get UI tree", e)
            return null
        }
    }

    /**
     * Find a node by text content.
     */
    fun findNodeByText(text: String): UINode? {
        val tree = getUITree() ?: return null
        return findNodeByTextRecursive(tree, text)
    }

    /**
     * Find a node by resource ID.
     */
    fun findNodeByResourceId(resourceId: String): UINode? {
        val tree = getUITree() ?: return null
        return findNodeByResourceIdRecursive(tree, resourceId)
    }

    /**
     * Tap at coordinates.
     */
    fun tapAt(x: Int, y: Int): Boolean {
        val service = accessibilityService ?: return false
        try {
            service.dispatchGesture(
                android.accessibilityservice.GestureDescription.Builder()
                    .addStroke(
                        android.accessibilityservice.GestureDescription.StrokeDescription(
                            android.graphics.Path().apply { moveTo(x.toFloat(), y.toFloat()) },
                            0, 100
                        )
                    )
                    .build(),
                null, null
            )
            return true
        } catch (e: Exception) {
            Log.e(TAG, "Tap failed", e)
            return false
        }
    }

    /**
     * Swipe from (startX, startY) to (endX, endY).
     */
    fun swipe(startX: Int, startY: Int, endX: Int, endY: Int, durationMs: Long = 300): Boolean {
        val service = accessibilityService ?: return false
        try {
            service.dispatchGesture(
                android.accessibilityservice.GestureDescription.Builder()
                    .addStroke(
                        android.accessibilityservice.GestureDescription.StrokeDescription(
                            android.graphics.Path().apply {
                                moveTo(startX.toFloat(), startY.toFloat())
                                lineTo(endX.toFloat(), endY.toFloat())
                            },
                            0, durationMs
                        )
                    )
                    .build(),
                null, null
            )
            return true
        } catch (e: Exception) {
            Log.e(TAG, "Swipe failed", e)
            return false
        }
    }

    /**
     * Type text into the currently focused field.
     */
    fun typeText(text: String): Boolean {
        val service = accessibilityService ?: return false
        try {
            val focusedNode = service.findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
            if (focusedNode != null) {
                val arguments = android.os.Bundle()
                arguments.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
                focusedNode.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
                return true
            }
            return false
        } catch (e: Exception) {
            Log.e(TAG, "Type text failed", e)
            return false
        }
    }

    /**
     * Press the back button.
     */
    fun pressBack(): Boolean {
        val service = accessibilityService ?: return false
        return service.performGlobalAction(AccessibilityService.GLOBAL_ACTION_BACK)
    }

    /**
     * Press the home button.
     */
    fun pressHome(): Boolean {
        val service = accessibilityService ?: return false
        return service.performGlobalAction(AccessibilityService.GLOBAL_ACTION_HOME)
    }

    private fun buildUINode(node: AccessibilityNodeInfo): UINode {
        val bounds = Rect()
        node.getBoundsInScreen(bounds)

        val children = mutableListOf<UINode>()
        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                children.add(buildUINode(child))
                child.recycle()
            }
        }

        return UINode(
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

    private fun findNodeByTextRecursive(node: UINode, text: String): UINode? {
        if (node.text.contains(text, ignoreCase = true) ||
            node.contentDescription.contains(text, ignoreCase = true)) {
            return node
        }
        for (child in node.children) {
            val found = findNodeByTextRecursive(child, text)
            if (found != null) return found
        }
        return null
    }

    private fun findNodeByResourceIdRecursive(node: UINode, resourceId: String): UINode? {
        if (node.resourceId == resourceId) return node
        for (child in node.children) {
            val found = findNodeByResourceIdRecursive(child, resourceId)
            if (found != null) return found
        }
        return null
    }

    data class UINode(
        val className: String = "",
        val text: String = "",
        val contentDescription: String = "",
        val resourceId: String = "",
        val isClickable: Boolean = false,
        val isFocusable: Boolean = false,
        val isPassword: Boolean = false,
        val bounds: List<Int> = emptyList(),
        val children: List<UINode> = emptyList(),
    )
}
