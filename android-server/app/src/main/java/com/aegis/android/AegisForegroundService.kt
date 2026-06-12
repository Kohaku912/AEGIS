package com.aegis.android

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.provider.DeviceProvider
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
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private lateinit var grpcClient: AegisGrpcClient
    private lateinit var deviceProvider: DeviceProvider

    override fun onCreate() {
        super.onCreate()
        Log.i(TAG, "Foreground service created")

        // Create notification channel and notification BEFORE startForeground
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, createNotification())

        grpcClient = AegisGrpcClient.getInstance()
        deviceProvider = DeviceProvider(this)

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

    private fun createNotification(): Notification {
        return Notification.Builder(this, CHANNEL_ID)
            .setContentTitle("AEGIS Android Server")
            .setContentText("Connected to AEGIS Core")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setOngoing(true)
            .build()
    }
}
