package com.aegis.android.overlay

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.PixelFormat
import android.net.Uri
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.util.Base64
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import com.aegis.android.MainActivity
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

class OverlayController(private val context: Context) {
    companion object {
        private const val CHANNEL_ID = "aegis_overlay"
        private const val APPROVAL_NOTIFICATION_ID = 2101
        private const val OVERLAY_NOTIFICATION_ID = 2102
    }

    private val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
    private val mainHandler = Handler(Looper.getMainLooper())
    private var overlayView: View? = null
    private var approvalView: View? = null

    data class ApprovalAction(
        val approvalId: String,
        val approved: Boolean,
        val rejected: Boolean,
        val globalReject: Boolean,
        val reason: String = "",
    )

    fun canDrawOverlays(): Boolean = Settings.canDrawOverlays(context)

    fun overlaySettingsIntent(): Intent {
        return Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:${context.packageName}"))
    }

    fun showText(text: String, durationMs: Long = 5000L): Boolean {
        return runOnMain { showTextOnMain(text, durationMs) }
    }

    fun showRichText(
        title: String,
        text: String,
        durationMs: Long = 5000L,
        imageBase64: String = "",
    ): Boolean {
        return runOnMain { showRichTextOnMain(title, text, durationMs, imageBase64) }
    }

    private fun showTextOnMain(text: String, durationMs: Long = 5000L): Boolean {
        if (!canDrawOverlays()) {
            showNotification("AEGIS", text, OVERLAY_NOTIFICATION_ID)
            return false
        }
        hideOverlay()
        val view = TextView(context).apply {
            this.text = text
            textSize = 16f
            setPadding(32, 24, 32, 24)
            setBackgroundColor(0xdd202124.toInt())
            setTextColor(0xffffffff.toInt())
        }
        overlayView = view
        windowManager.addView(view, params(Gravity.TOP or Gravity.CENTER_HORIZONTAL))
        view.postDelayed({ hideOverlay() }, durationMs.coerceAtLeast(1000L))
        return true
    }

    private fun showRichTextOnMain(
        title: String,
        text: String,
        durationMs: Long = 5000L,
        imageBase64: String = "",
    ): Boolean {
        val bitmap = decodeImage(imageBase64)
        if (!canDrawOverlays()) {
            showNotification(title.ifBlank { "AEGIS" }, text, OVERLAY_NOTIFICATION_ID, bitmap)
            return false
        }
        hideOverlay()
        val root = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 24, 32, 24)
            setBackgroundColor(0xee202124.toInt())
        }
        root.addView(TextView(context).apply {
            this.text = title.ifBlank { "AEGIS" }
            textSize = 18f
            setTextColor(0xffffffff.toInt())
        })
        root.addView(TextView(context).apply {
            this.text = text
            textSize = 15f
            setPadding(0, 10, 0, 12)
            setTextColor(0xffe8eaed.toInt())
        })
        if (bitmap != null) {
            root.addView(ImageView(context).apply {
                setImageBitmap(bitmap)
                adjustViewBounds = true
                maxWidth = 720
                maxHeight = 520
                scaleType = ImageView.ScaleType.FIT_CENTER
            })
        }
        overlayView = root
        windowManager.addView(root, params(Gravity.TOP or Gravity.CENTER_HORIZONTAL))
        root.postDelayed({ hideOverlay() }, durationMs.coerceAtLeast(1000L))
        return true
    }

    fun showApproval(
        approvalId: String,
        title: String,
        body: String,
        onDecision: (ApprovalAction) -> Unit,
    ): Boolean {
        return runOnMain { showApprovalOnMain(approvalId, title, body, onDecision) }
    }

    private fun showApprovalOnMain(
        approvalId: String,
        title: String,
        body: String,
        onDecision: (ApprovalAction) -> Unit,
    ): Boolean {
        if (!canDrawOverlays()) {
            showNotification(title, body, APPROVAL_NOTIFICATION_ID)
            return false
        }
        hideApproval()
        val root = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 28, 32, 28)
            setBackgroundColor(0xee202124.toInt())
        }
        root.addView(TextView(context).apply {
            text = title
            textSize = 18f
            setTextColor(0xffffffff.toInt())
        })
        root.addView(TextView(context).apply {
            text = body
            textSize = 14f
            setTextColor(0xffe8eaed.toInt())
            setPadding(0, 12, 0, 16)
        })
        val buttons = LinearLayout(context).apply {
            orientation = LinearLayout.HORIZONTAL
        }
        buttons.addView(Button(context).apply {
            text = "Approve"
            setOnClickListener {
                hideApproval()
                onDecision(ApprovalAction(approvalId, approved = true, rejected = false, globalReject = false))
            }
        })
        buttons.addView(Button(context).apply {
            text = "Reject"
            setOnClickListener {
                hideApproval()
                onDecision(ApprovalAction(approvalId, approved = false, rejected = true, globalReject = false))
            }
        })
        buttons.addView(Button(context).apply {
            text = "Reject All"
            setOnClickListener {
                hideApproval()
                onDecision(ApprovalAction(approvalId, approved = false, rejected = true, globalReject = true))
            }
        })
        root.addView(buttons)
        approvalView = root
        windowManager.addView(root, params(Gravity.TOP or Gravity.CENTER_HORIZONTAL))
        return true
    }

    fun hideOverlay() {
        if (Looper.myLooper() != Looper.getMainLooper()) {
            mainHandler.post { hideOverlay() }
            return
        }
        overlayView?.let { runCatching { windowManager.removeView(it) } }
        overlayView = null
    }

    fun hideApproval() {
        if (Looper.myLooper() != Looper.getMainLooper()) {
            mainHandler.post { hideApproval() }
            return
        }
        approvalView?.let { runCatching { windowManager.removeView(it) } }
        approvalView = null
    }

    fun emergencyStop() {
        hideOverlay()
        hideApproval()
    }

    private fun params(gravity: Int): WindowManager.LayoutParams {
        val type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }
        return WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            type,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT,
        ).apply {
            this.gravity = gravity
            y = 96
        }
    }

    private fun showNotification(title: String, body: String, id: Int, bitmap: Bitmap? = null) {
        val manager = context.getSystemService(NotificationManager::class.java)
        val channel = NotificationChannel(CHANNEL_ID, "AEGIS Overlay", NotificationManager.IMPORTANCE_HIGH)
        manager.createNotificationChannel(channel)
        val intent = Intent(context, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context,
            id,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val builder = Notification.Builder(context, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(body)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
        if (bitmap != null) {
            builder.setStyle(Notification.BigPictureStyle().bigPicture(bitmap).setSummaryText(body))
        }
        manager.notify(id, builder.build())
    }

    private fun decodeImage(imageBase64: String): Bitmap? {
        if (imageBase64.isBlank()) return null
        return runCatching {
            val bytes = Base64.decode(imageBase64, Base64.DEFAULT)
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
        }.getOrNull()
    }

    private fun runOnMain(block: () -> Boolean): Boolean {
        if (Looper.myLooper() == Looper.getMainLooper()) {
            return block()
        }
        val result = AtomicReference(false)
        val latch = CountDownLatch(1)
        mainHandler.post {
            result.set(runCatching { block() }.getOrDefault(false))
            latch.countDown()
        }
        latch.await(3, TimeUnit.SECONDS)
        return result.get()
    }
}
