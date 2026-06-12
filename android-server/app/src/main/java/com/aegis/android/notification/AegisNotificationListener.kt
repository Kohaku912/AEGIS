package com.aegis.android.notification

import android.app.Notification
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
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
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var grpcClient: AegisGrpcClient? = null

    override fun onCreate() {
        super.onCreate()
        Log.i(TAG, "NotificationListener created")
        grpcClient = AegisGrpcClient.getInstance()
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

        // Push to AEGIS Core via gRPC
        scope.launch {
            try {
                grpcClient?.pushNotification(
                    packageName = packageName,
                    appName = packageName.substringAfterLast('.'),
                    title = title,
                    text = text,
                    postedMs = sbn.postTime,
                    isOngoing = (notification.flags and Notification.FLAG_ONGOING_EVENT) != 0,
                    isClearable = (notification.flags and Notification.FLAG_NO_CLEAR) == 0,
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
