package com.aegis.android.provider

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import androidx.core.content.ContextCompat

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
        val providers = listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER, LocationManager.PASSIVE_PROVIDER)
        val best = providers
            .filter { manager.isProviderEnabled(it) }
            .mapNotNull { provider -> runCatching { manager.getLastKnownLocation(provider) }.getOrNull() }
            .maxByOrNull { it.time }
            ?: return null
        return best.toResult()
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
