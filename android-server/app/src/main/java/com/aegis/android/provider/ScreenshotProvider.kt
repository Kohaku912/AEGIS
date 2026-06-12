package com.aegis.android.provider

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.Image
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Handler
import android.os.Looper
import android.util.Base64
import android.util.DisplayMetrics
import android.util.Log
import android.view.WindowManager
import java.io.ByteArrayOutputStream
import java.util.concurrent.CompletableFuture
import java.util.concurrent.TimeUnit

/**
 * Screenshot provider using MediaProjection.
 *
 * Requires user to grant screen capture permission via Activity.
 * The MediaProjection token is obtained from the Activity result.
 */
class ScreenshotProvider(private val context: Context) {

    companion object {
        private const val TAG = "ScreenshotProvider"
        private const val VIRTUAL_DISPLAY_NAME = "AEGIS_Screenshot"
    }

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null

    /**
     * Set the MediaProjection result from Activity.
     * Call this from Activity.onActivityResult.
     */
    fun setMediaProjectionResult(resultCode: Int, data: Intent) {
        val projectionManager = context.getSystemService(
            Context.MEDIA_PROJECTION_SERVICE
        ) as MediaProjectionManager
        mediaProjection = projectionManager.getMediaProjection(resultCode, data)
        Log.i(TAG, "MediaProjection initialized")
    }

    /**
     * Check if MediaProjection is available.
     */
    fun isAvailable(): Boolean {
        return mediaProjection != null
    }

    /**
     * Capture a screenshot and return as base64.
     * Returns null if MediaProjection is not available.
     */
    fun captureScreenshot(): ScreenshotResult? {
        val projection = mediaProjection ?: run {
            Log.w(TAG, "MediaProjection not available")
            return null
        }

        try {
            val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
            val metrics = DisplayMetrics()
            @Suppress("DEPRECATION")
            windowManager.defaultDisplay.getRealMetrics(metrics)

            val width = metrics.widthPixels
            val height = metrics.heightPixels
            val density = metrics.densityDpi

            imageReader = ImageReader.newInstance(width, height, PixelFormat.RGBA_8888, 1)

            virtualDisplay = projection.createVirtualDisplay(
                VIRTUAL_DISPLAY_NAME,
                width, height, density,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                imageReader!!.surface,
                null, Handler(Looper.getMainLooper())
            )

            // Wait for image to be available
            Thread.sleep(500)

            val image = imageReader?.acquireLatestImage()
            if (image == null) {
                Log.w(TAG, "No image available")
                return null
            }

            val bitmap = imageToBitmap(image, width, height)
            image.close()

            val base64 = bitmapToBase64(bitmap)
            bitmap.recycle()

            // Clean up
            virtualDisplay?.release()
            imageReader?.close()

            return ScreenshotResult(
                width = width,
                height = height,
                imageBase64 = base64,
                format = "png",
                capturedAtMs = System.currentTimeMillis()
            )

        } catch (e: Exception) {
            Log.e(TAG, "Screenshot failed", e)
            return null
        }
    }

    private fun imageToBitmap(image: Image, width: Int, height: Int): android.graphics.Bitmap {
        val plane = image.planes[0]
        val buffer = plane.buffer
        val pixelStride = plane.pixelStride
        val rowStride = plane.rowStride
        val rowPadding = rowStride - pixelStride * width

        val bitmap = android.graphics.Bitmap.createBitmap(
            width + rowPadding / pixelStride,
            height,
            android.graphics.Bitmap.Config.ARGB_8888
        )
        bitmap.copyPixelsFromBuffer(buffer)
        return android.graphics.Bitmap.createBitmap(bitmap, 0, 0, width, height)
    }

    private fun bitmapToBase64(bitmap: android.graphics.Bitmap): String {
        val stream = ByteArrayOutputStream()
        bitmap.compress(android.graphics.Bitmap.CompressFormat.PNG, 100, stream)
        val bytes = stream.toByteArray()
        return Base64.encodeToString(bytes, Base64.NO_WRAP)
    }

    data class ScreenshotResult(
        val width: Int,
        val height: Int,
        val imageBase64: String,
        val format: String,
        val capturedAtMs: Long,
    )
}
