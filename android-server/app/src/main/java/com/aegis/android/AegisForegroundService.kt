package com.aegis.android

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.RemoteInput
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.provider.DeviceProvider
import com.aegis.android.provider.UserActivityCollector
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * Foreground service that maintains the gRPC connection to AEGIS Core
 * and periodically pushes device state.
 */
class AegisForegroundService : Service() {

    companion object {
        private const val TAG = "AegisForegroundSvc"
        private const val CHANNEL_ID = "aegis_service_channel"
        private const val NOTIFICATION_ID = 1001
        private const val DEVICE_STATE_INTERVAL_MS = 60_000L // 1 minute
        private const val ACTION_CHAT_REPLY = "com.aegis.android.action.CHAT_REPLY"
        private const val KEY_CHAT_REPLY = "aegis_chat_reply"
        private val RECONNECT_DELAYS_MS = longArrayOf(2_000L, 5_000L, 10_000L, 30_000L)
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private lateinit var grpcClient: AegisGrpcClient
    private lateinit var deviceProvider: DeviceProvider
    private lateinit var userActivityCollector: UserActivityCollector
    private var notificationConversationId = "android_notification_${System.currentTimeMillis()}"

    override fun onCreate() {
        super.onCreate()
        Log.i(TAG, "Foreground service created")

        // Create notification channel and notification BEFORE startForeground
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, createNotification())

        grpcClient = AegisGrpcClient.getInstance(this)
        deviceProvider = DeviceProvider(this)
        userActivityCollector = UserActivityCollector(this)

        scope.launch {
            var delayIndex = 0
            while (isActive) {
                try {
                    if (!grpcClient.isConnected()) {
                        val waitMs = RECONNECT_DELAYS_MS[delayIndex.coerceAtMost(RECONNECT_DELAYS_MS.lastIndex)]
                        grpcClient.setNextRetry(System.currentTimeMillis())
                        val success = grpcClient.connect()
                        if (success) {
                            delayIndex = 0
                            delay(5_000L)
                        } else {
                            delayIndex = (delayIndex + 1).coerceAtMost(RECONNECT_DELAYS_MS.lastIndex)
                            grpcClient.setNextRetry(System.currentTimeMillis() + waitMs)
                            delay(waitMs)
                        }
                    } else {
                        delayIndex = 0
                        delay(5_000L)
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Reconnect loop error", e)
                    val waitMs = RECONNECT_DELAYS_MS[delayIndex.coerceAtMost(RECONNECT_DELAYS_MS.lastIndex)]
                    delayIndex = (delayIndex + 1).coerceAtMost(RECONNECT_DELAYS_MS.lastIndex)
                    grpcClient.setNextRetry(System.currentTimeMillis() + waitMs)
                    delay(waitMs)
                }
            }
        }

        // Start periodic device state push
        scope.launch {
            while (isActive) {
                try {
                    if (grpcClient.isConnected()) {
                        val device = deviceProvider.getDeviceInfo()
                        grpcClient.pushDeviceState(
                            batteryLevel = device.batteryLevel,
                            screenOn = device.screenOn,
                        )
                        userActivityCollector.collectIfChanged()?.let { payload ->
                            grpcClient.pushUserActivity(payload.toString())
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error pushing device state", e)
                }
                delay(DEVICE_STATE_INTERVAL_MS)
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.i(TAG, "Foreground service started")
        grpcClient = AegisGrpcClient.getInstance(this)
        if (intent?.action == ACTION_CHAT_REPLY) {
            val message = RemoteInput.getResultsFromIntent(intent)
                ?.getCharSequence(KEY_CHAT_REPLY)
                ?.toString()
                ?.trim()
                .orEmpty()
            if (message.isNotEmpty()) {
                sendNotificationChat(message)
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.i(TAG, "Foreground service destroyed")
        scope.cancel()
        grpcClient.disconnect()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "AEGIS Connection",
            NotificationManager.IMPORTANCE_LOW,
        ).apply {
            description = "Maintains connection to AEGIS Core"
        }
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }

    private fun createNotification(content: String = "Maintaining AEGIS Core connection"): Notification {
        val openAppIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val replyIntent = PendingIntent.getService(
            this,
            1,
            Intent(this, AegisForegroundService::class.java).setAction(ACTION_CHAT_REPLY),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_MUTABLE,
        )
        val remoteInput = RemoteInput.Builder(KEY_CHAT_REPLY)
            .setLabel("Message AEGIS")
            .build()
        val replyAction = NotificationCompat.Action.Builder(
            android.R.drawable.ic_menu_send,
            "Reply",
            replyIntent,
        )
            .addRemoteInput(remoteInput)
            .setAllowGeneratedReplies(true)
            .build()

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("AEGIS Android Server")
            .setContentText(content)
            .setStyle(NotificationCompat.BigTextStyle().bigText(content))
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentIntent(openAppIntent)
            .setCategory(NotificationCompat.CATEGORY_MESSAGE)
            .setOnlyAlertOnce(true)
            .setOngoing(true)
            .addAction(replyAction)
            .build()
    }

    private fun sendNotificationChat(message: String) {
        updateNotification("Sending to AEGIS...")
        scope.launch {
            val reply = grpcClient.sendChat(message, notificationConversationId)
            notificationConversationId = reply.conversationId.ifBlank { notificationConversationId }
            val content = when {
                !reply.ok -> "Chat failed: ${reply.error}"
                reply.approvalNeeded -> reply.response.ifBlank { "Approval required: ${reply.approvalId}" }
                reply.response.isNotBlank() -> reply.response
                else -> "AEGIS returned an empty response"
            }
            updateNotification(content)
        }
    }

    private fun updateNotification(content: String) {
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, createNotification(content))
    }
}
