package com.aegis.android.notification

import android.app.Notification
import android.content.ComponentName
import android.content.Context
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.provider.Settings
import android.text.TextUtils
import android.util.Log
import com.aegis.android.grpc.AegisGrpcClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

/**
 * NotificationListenerService that captures Android notifications
 * and pushes them to AEGIS Core via gRPC.
 *
 * User must enable notification access in Settings:
 * Settings → Apps → Special app access → Notification access → AEGIS Android
 */
class AegisNotificationListener : NotificationListenerService() {

    companion object {
        private const val TAG = "AegisNotifListener"

        // Packages to ignore (system noise, self)
        private val IGNORED_PACKAGES = setOf(
            "com.aegis.android",
            "android",
            "com.android.systemui",
        )

        private const val MAX_RECENT = 100
        private val recent = ArrayDeque<NotificationItem>()

        fun isEnabled(context: Context): Boolean {
            val flat = Settings.Secure.getString(context.contentResolver, "enabled_notification_listeners")
            if (TextUtils.isEmpty(flat)) return false
            val component = ComponentName(context, AegisNotificationListener::class.java).flattenToString()
            return flat.split(":").any { it == component }
        }

        fun requestReconnect(context: Context) {
            if (!isEnabled(context)) return
            val component = ComponentName(context, AegisNotificationListener::class.java)
            runCatching { requestRebind(component) }
                .onFailure { Log.w(TAG, "NotificationListener rebind request failed", it) }
        }

        fun recentNotifications(maxCount: Int): List<NotificationItem> {
            synchronized(recent) {
                return recent.take(maxCount)
            }
        }
    }

    data class NotificationItem(
        val key: String,
        val packageName: String,
        val appName: String,
        val title: String,
        val text: String,
        val postedMs: Long,
        val isOngoing: Boolean,
        val isClearable: Boolean,
    )

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var grpcClient: AegisGrpcClient? = null

    override fun onCreate() {
        super.onCreate()
        Log.i(TAG, "NotificationListener created")
        grpcClient = AegisGrpcClient.getInstance(this)
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.i(TAG, "NotificationListener destroyed")
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        sbn ?: return

        val packageName = sbn.packageName
        if (packageName in IGNORED_PACKAGES) return

        val notification = sbn.notification
        val extras = notification.extras

        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString() ?: ""
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString() ?: ""

        if (title.isEmpty() && text.isEmpty()) return

        Log.d(TAG, "Notification: pkg=$packageName title=$title")
        val item = NotificationItem(
            key = sbn.key,
            packageName = packageName,
            appName = packageName.substringAfterLast('.'),
            title = title,
            text = text,
            postedMs = sbn.postTime,
            isOngoing = (notification.flags and Notification.FLAG_ONGOING_EVENT) != 0,
            isClearable = (notification.flags and Notification.FLAG_NO_CLEAR) == 0,
        )
        synchronized(recent) {
            recent.addFirst(item)
            while (recent.size > MAX_RECENT) {
                recent.removeLast()
            }
        }

        // Push to AEGIS Core via gRPC
        scope.launch {
            try {
                grpcClient?.pushNotification(
                    packageName = item.packageName,
                    appName = item.appName,
                    title = item.title,
                    text = item.text,
                    postedMs = item.postedMs,
                    isOngoing = item.isOngoing,
                    isClearable = item.isClearable,
                )
            } catch (e: Exception) {
                Log.e(TAG, "Failed to push notification to AEGIS Core", e)
            }
        }
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification?) {
        // Could track notification dismissal — future enhancement
    }
}
