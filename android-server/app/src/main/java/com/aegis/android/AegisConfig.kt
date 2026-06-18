package com.aegis.android

import android.content.Context
import android.provider.Settings
import java.util.UUID

data class AegisConnectionConfig(
    val host: String,
    val port: Int,
    val pairingToken: String,
    val deviceId: String,
)

object AegisConfig {
    private const val PREFS = "aegis_android_config"
    private const val KEY_HOST = "host"
    private const val KEY_PORT = "port"
    private const val KEY_PAIRING_TOKEN = "pairing_token"
    private const val KEY_DEVICE_ID = "device_id"

    private const val DEFAULT_HOST = "192.168.50.175"
    private const val DEFAULT_PORT = 50051

    fun load(context: Context): AegisConnectionConfig {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val androidId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
        val fallbackId = "android-${androidId ?: UUID.randomUUID().toString()}"
        val deviceId = prefs.getString(KEY_DEVICE_ID, null) ?: fallbackId.also {
            prefs.edit().putString(KEY_DEVICE_ID, it).apply()
        }
        return AegisConnectionConfig(
            host = prefs.getString(KEY_HOST, DEFAULT_HOST) ?: DEFAULT_HOST,
            port = prefs.getInt(KEY_PORT, DEFAULT_PORT),
            pairingToken = prefs.getString(KEY_PAIRING_TOKEN, "") ?: "",
            deviceId = deviceId,
        )
    }

    fun save(context: Context, host: String, port: Int, pairingToken: String): AegisConnectionConfig {
        val current = load(context)
        val cleanHost = host.trim().ifEmpty { DEFAULT_HOST }
        val cleanPort = port.takeIf { it in 1..65535 } ?: DEFAULT_PORT
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_HOST, cleanHost)
            .putInt(KEY_PORT, cleanPort)
            .putString(KEY_PAIRING_TOKEN, pairingToken)
            .putString(KEY_DEVICE_ID, current.deviceId)
            .apply()
        return AegisConnectionConfig(cleanHost, cleanPort, pairingToken, current.deviceId)
    }
}
