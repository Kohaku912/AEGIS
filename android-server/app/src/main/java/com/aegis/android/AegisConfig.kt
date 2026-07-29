package com.aegis.android

import android.content.Context
import android.provider.Settings
import java.util.UUID

data class AegisConnectionConfig(
    val host: String,
    val port: Int,
    val pairingToken: String,
    val deviceId: String,
    /** Optional alternate host; leave blank when Cloudflare WARP reaches [host] directly. */
    val fallbackHost: String = "",
    val fallbackPort: Int = DEFAULT_PORT,
    val useTlsFallback: Boolean = false,
    val cfAccessClientId: String = "",
    val cfAccessClientSecret: String = "",
    val lastWorkingHost: String = "",
    val lastWorkingPort: Int = 0,
    val lastWorkingTls: Boolean = false,
) {
    fun primaryUsesTls(): Boolean = port == 443

    fun fallbackUsesTls(): Boolean = useTlsFallback || fallbackPort == 443

    fun endpointsPreferringWifi(wifi: Boolean): List<Endpoint> {
        val primary = Endpoint(host, port, primaryUsesTls(), "primary")
        val fallback = if (fallbackHost.isNotBlank()) {
            Endpoint(fallbackHost, fallbackPort, fallbackUsesTls(), "fallback")
        } else {
            null
        }
        val last = if (lastWorkingHost.isNotBlank() && lastWorkingPort in 1..65535) {
            Endpoint(lastWorkingHost, lastWorkingPort, lastWorkingTls, "last")
        } else {
            null
        }
        val ordered = mutableListOf<Endpoint>()
        if (last != null) ordered.add(last)
        if (wifi) {
            ordered.add(primary)
            if (fallback != null) ordered.add(fallback)
        } else {
            // Cellular: same Core LAN IP via Cloudflare WARP private network.
            ordered.add(primary)
            if (fallback != null) ordered.add(fallback)
        }
        return ordered.distinctBy { "${it.host}:${it.port}:${it.useTls}" }
    }

    companion object {
        const val DEFAULT_PORT: Int = 50051
    }
}

data class Endpoint(
    val host: String,
    val port: Int,
    val useTls: Boolean,
    val label: String,
)

object AegisConfig {
    private const val PREFS = "aegis_android_config"
    private const val KEY_HOST = "host"
    private const val KEY_PORT = "port"
    private const val KEY_PAIRING_TOKEN = "pairing_token"
    private const val KEY_DEVICE_ID = "device_id"
    private const val KEY_FALLBACK_HOST = "fallback_host"
    private const val KEY_FALLBACK_PORT = "fallback_port"
    private const val KEY_USE_TLS_FALLBACK = "use_tls_fallback"
    private const val KEY_CF_ACCESS_CLIENT_ID = "cf_access_client_id"
    private const val KEY_CF_ACCESS_CLIENT_SECRET = "cf_access_client_secret"
    private const val KEY_LAST_HOST = "last_working_host"
    private const val KEY_LAST_PORT = "last_working_port"
    private const val KEY_LAST_TLS = "last_working_tls"

    private const val DEFAULT_HOST = "192.168.50.41"
    private const val DEFAULT_PORT = AegisConnectionConfig.DEFAULT_PORT
    /** Deprecated public gRPC hostname (Free plan blocks application/grpc). */
    private const val LEGACY_PUBLIC_GRPC_HOST = "grpc.kawahara.pp.ua"

    const val DEFAULT_FALLBACK_HOST = ""
    const val DEFAULT_FALLBACK_PORT = DEFAULT_PORT

    fun load(context: Context): AegisConnectionConfig {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val androidId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
        val fallbackId = "android-${androidId ?: UUID.randomUUID().toString()}"
        val deviceId = prefs.getString(KEY_DEVICE_ID, null) ?: fallbackId.also {
            prefs.edit().putString(KEY_DEVICE_ID, it).apply()
        }
        val rawFallback = prefs.getString(KEY_FALLBACK_HOST, DEFAULT_FALLBACK_HOST) ?: DEFAULT_FALLBACK_HOST
        val fallbackHost = if (rawFallback.equals(LEGACY_PUBLIC_GRPC_HOST, ignoreCase = true)) {
            ""
        } else {
            rawFallback
        }
        return AegisConnectionConfig(
            host = prefs.getString(KEY_HOST, DEFAULT_HOST) ?: DEFAULT_HOST,
            port = prefs.getInt(KEY_PORT, DEFAULT_PORT),
            pairingToken = prefs.getString(KEY_PAIRING_TOKEN, "") ?: "",
            deviceId = deviceId,
            fallbackHost = fallbackHost,
            fallbackPort = prefs.getInt(KEY_FALLBACK_PORT, DEFAULT_FALLBACK_PORT),
            useTlsFallback = prefs.getBoolean(KEY_USE_TLS_FALLBACK, false),
            cfAccessClientId = prefs.getString(KEY_CF_ACCESS_CLIENT_ID, "") ?: "",
            cfAccessClientSecret = prefs.getString(KEY_CF_ACCESS_CLIENT_SECRET, "") ?: "",
            lastWorkingHost = prefs.getString(KEY_LAST_HOST, "") ?: "",
            lastWorkingPort = prefs.getInt(KEY_LAST_PORT, 0),
            lastWorkingTls = prefs.getBoolean(KEY_LAST_TLS, false),
        )
    }

    fun save(
        context: Context,
        host: String,
        port: Int,
        pairingToken: String,
        fallbackHost: String? = null,
        fallbackPort: Int? = null,
        useTlsFallback: Boolean? = null,
        cfAccessClientId: String? = null,
        cfAccessClientSecret: String? = null,
    ): AegisConnectionConfig {
        val current = load(context)
        val cleanHost = host.trim().ifEmpty { DEFAULT_HOST }
        val cleanPort = port.takeIf { it in 1..65535 } ?: DEFAULT_PORT
        // Allow blank fallback to disable secondary endpoint (WARP path).
        val cleanFallbackHost = when {
            fallbackHost != null -> {
                val trimmed = fallbackHost.trim()
                if (trimmed.equals(LEGACY_PUBLIC_GRPC_HOST, ignoreCase = true)) "" else trimmed
            }
            else -> current.fallbackHost
        }
        val cleanFallbackPort = (fallbackPort ?: current.fallbackPort).takeIf { it in 1..65535 } ?: DEFAULT_FALLBACK_PORT
        val cleanTls = useTlsFallback ?: current.useTlsFallback
        val cleanId = cfAccessClientId ?: current.cfAccessClientId
        val cleanSecret = cfAccessClientSecret ?: current.cfAccessClientSecret
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_HOST, cleanHost)
            .putInt(KEY_PORT, cleanPort)
            .putString(KEY_PAIRING_TOKEN, pairingToken)
            .putString(KEY_DEVICE_ID, current.deviceId)
            .putString(KEY_FALLBACK_HOST, cleanFallbackHost)
            .putInt(KEY_FALLBACK_PORT, cleanFallbackPort)
            .putBoolean(KEY_USE_TLS_FALLBACK, cleanTls)
            .putString(KEY_CF_ACCESS_CLIENT_ID, cleanId)
            .putString(KEY_CF_ACCESS_CLIENT_SECRET, cleanSecret)
            .apply()
        return AegisConnectionConfig(
            cleanHost,
            cleanPort,
            pairingToken,
            current.deviceId,
            cleanFallbackHost,
            cleanFallbackPort,
            cleanTls,
            cleanId,
            cleanSecret,
            current.lastWorkingHost,
            current.lastWorkingPort,
            current.lastWorkingTls,
        )
    }

    fun rememberWorkingEndpoint(context: Context, host: String, port: Int, useTls: Boolean) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_LAST_HOST, host)
            .putInt(KEY_LAST_PORT, port)
            .putBoolean(KEY_LAST_TLS, useTls)
            .apply()
    }
}
