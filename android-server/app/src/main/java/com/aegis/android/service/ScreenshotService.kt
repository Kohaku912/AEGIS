package com.aegis.android.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log

/**
 * Foreground service required for MediaProjection (screenshots).
 * Android requires a foreground service with MEDIA_PROJECTION type
 * to capture screen content.
 */
class ScreenshotService : Service() {

    companion object {
        private const val TAG = "ScreenshotService"
        private const val CHANNEL_ID = "aegis_screenshot_channel"
        private const val NOTIFICATION_ID = 1002
    }

    override fun onCreate() {
        super.onCreate()
        Log.i(TAG, "ScreenshotService created")
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, createNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.i(TAG, "ScreenshotService started")
        return START_NOT_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.i(TAG, "ScreenshotService destroyed")
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "AEGIS Screenshot",
            NotificationManager.IMPORTANCE_LOW,
        ).apply {
            description = "Required for screen capture"
        }
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }

    private fun createNotification(): Notification {
        return Notification.Builder(this, CHANNEL_ID)
            .setContentTitle("AEGIS Screenshot")
            .setContentText("Screen capture active")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setOngoing(true)
            .build()
    }
}
