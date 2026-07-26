package com.aegis.android.provider

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import android.os.Build
import android.os.CancellationSignal
import androidx.core.content.ContextCompat
import java.util.concurrent.CompletableFuture
import java.util.concurrent.TimeUnit

class LocationProvider(private val context: Context) {
    data class LocationResult(
        val latitude: Double,
        val longitude: Double,
        val accuracyMeters: Float,
        val capturedMs: Long,
    )

    fun hasPermission(): Boolean {
        return ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED ||
            ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED
    }

    @SuppressLint("MissingPermission")
    fun getCurrentLocation(): LocationResult? {
        if (!hasPermission()) return null
        val manager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        val providers = listOf(
            LocationManager.GPS_PROVIDER,
            LocationManager.NETWORK_PROVIDER,
            LocationManager.PASSIVE_PROVIDER,
        )
        val enabledProviders = providers.filter { manager.isProviderEnabled(it) }
        val lastKnown = getLastKnownLocation(manager, enabledProviders)

        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) {
            return lastKnown?.toResult()
        }

        val future = CompletableFuture<Location>()
        val signals = mutableListOf<CancellationSignal>()
        enabledProviders
            .filter { it != LocationManager.PASSIVE_PROVIDER }
            .forEach { provider ->
                val signal = CancellationSignal()
                signals += signal
                runCatching {
                    manager.getCurrentLocation(
                        provider,
                        signal,
                        context.mainExecutor,
                    ) { location ->
                        if (location != null) future.complete(location)
                    }
                }
            }
        val current = runCatching {
            future.get(12, TimeUnit.SECONDS)
        }.getOrNull()
        signals.forEach(CancellationSignal::cancel)
        return (current ?: lastKnown)?.toResult()
    }

    /**
     * Returns cached location without waiting for a fresh sensor fix.
     *
     * This method is safe for accessibility callbacks, which Android invokes on
     * the main thread and must never be blocked by a live location request.
     */
    @SuppressLint("MissingPermission")
    fun getLastKnownLocation(): LocationResult? {
        if (!hasPermission()) return null
        val manager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        val providers = listOf(
            LocationManager.GPS_PROVIDER,
            LocationManager.NETWORK_PROVIDER,
            LocationManager.PASSIVE_PROVIDER,
        ).filter { manager.isProviderEnabled(it) }
        return getLastKnownLocation(manager, providers)?.toResult()
    }

    @SuppressLint("MissingPermission")
    private fun getLastKnownLocation(
        manager: LocationManager,
        providers: List<String>,
    ): Location? {
        return providers
            .mapNotNull { provider ->
                runCatching { manager.getLastKnownLocation(provider) }.getOrNull()
            }
            .maxByOrNull { it.time }
    }

    private fun Location.toResult(): LocationResult {
        return LocationResult(
            latitude = latitude,
            longitude = longitude,
            accuracyMeters = accuracy,
            capturedMs = time.takeIf { it > 0 } ?: System.currentTimeMillis(),
        )
    }
}
