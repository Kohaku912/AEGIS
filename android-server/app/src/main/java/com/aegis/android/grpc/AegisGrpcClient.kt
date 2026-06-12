package com.aegis.android.grpc

import android.util.Log
import aegis.AIServerGrpc
import aegis.AIServerGrpcKt
import aegis.AiServer
import aegis.Common
import aegis.serverInfo
import aegis.capability
import aegis.event
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import io.grpc.StatusRuntimeException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.concurrent.TimeUnit

/**
 * gRPC client for communicating with AEGIS Core (AI Server).
 */
class AegisGrpcClient private constructor(
    private val host: String,
    private val port: Int,
) {
    companion object {
        private const val TAG = "AegisGrpcClient"
        private const val DEFAULT_HOST = "192.168.50.175"
        private const val DEFAULT_PORT = 50051

        @Volatile
        private var instance: AegisGrpcClient? = null

        fun getInstance(host: String = DEFAULT_HOST, port: Int = DEFAULT_PORT): AegisGrpcClient {
            return instance ?: synchronized(this) {
                instance ?: AegisGrpcClient(host, port).also { instance = it }
            }
        }
    }

    private var channel: ManagedChannel? = null
    private var stub: AIServerGrpcKt.AIServerCoroutineStub? = null
    private var connected = false

    suspend fun connect(): Boolean = withContext(Dispatchers.IO) {
        try {
            channel = ManagedChannelBuilder
                .forAddress(host, port)
                .usePlaintext()
                .keepAliveTime(30, TimeUnit.SECONDS)
                .build()

            stub = AIServerGrpcKt.AIServerCoroutineStub(channel!!)

            val healthRequest = Common.HealthCheckRequest.getDefaultInstance()
            val healthResponse = stub!!.healthCheck(healthRequest)
            if (healthResponse.status.code == 0) {
                connected = true
                Log.i(TAG, "Connected to AEGIS Core at $host:$port (v${healthResponse.version})")
                true
            } else {
                Log.e(TAG, "Health check failed: ${healthResponse.status.message}")
                connected = false
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to connect to AEGIS Core", e)
            connected = false
            false
        }
    }

    fun disconnect() {
        try {
            channel?.shutdown()?.awaitTermination(5, TimeUnit.SECONDS)
        } catch (e: Exception) {
            Log.e(TAG, "Error disconnecting", e)
        } finally {
            channel = null
            stub = null
            connected = false
        }
    }

    suspend fun registerCapabilities(): Boolean = withContext(Dispatchers.IO) {
        if (!connected || stub == null) {
            Log.w(TAG, "Not connected - cannot register capabilities")
            return@withContext false
        }

        try {
            val serverInfoObj = serverInfo {
                serverId = "android-server-main"
                serverType = Common.ServerType.SERVER_TYPE_ANDROID
                version = "0.1.0"
                status = Common.ServerStatus.SERVER_STATUS_ONLINE
                capabilityIds.addAll(listOf(
                    "android.get_notifications",
                    "android.get_current_app",
                    "android.get_device_info",
                    "android.get_screenshot",
                    "android.get_ui_tree",
                    "android.show_overlay",
                    "android.hide_overlay",
                    "android.open_app",
                    "android.press_home",
                ))
                host = this@AegisGrpcClient.host
                port = this@AegisGrpcClient.port
                startedAtMs = System.currentTimeMillis()
            }

            val registerRequest = AiServer.RegisterServerRequest.newBuilder()
                .setServerInfo(serverInfoObj)
                .build()

            val response = stub!!.registerServer(registerRequest)
            if (response.status.code != 0) {
                Log.e(TAG, "Failed to register server: ${response.status.message}")
                return@withContext false
            }

            val caps = listOf(
                buildCapability("android.get_notifications", "Get Notifications",
                    "Retrieve current status bar notifications.", Common.SafetyLevel.LEVEL_0_READ),
                buildCapability("android.get_current_app", "Get Current App",
                    "Return the package name and activity of the foreground app.", Common.SafetyLevel.LEVEL_0_READ),
                buildCapability("android.get_device_info", "Get Device Info",
                    "Return device model, Android version, battery level.", Common.SafetyLevel.LEVEL_0_READ),
                buildCapability("android.get_screenshot", "Get Screenshot",
                    "Capture screenshot via MediaProjection.", Common.SafetyLevel.LEVEL_0_READ),
                buildCapability("android.get_ui_tree", "Get UI Tree",
                    "Get current UI tree via AccessibilityService.", Common.SafetyLevel.LEVEL_0_READ),
                buildCapability("android.show_overlay", "Show Overlay",
                    "Show an overlay notification on the device.", Common.SafetyLevel.LEVEL_1_SAFE_ACT),
                buildCapability("android.hide_overlay", "Hide Overlay",
                    "Hide the current overlay notification.", Common.SafetyLevel.LEVEL_1_SAFE_ACT),
                buildCapability("android.open_app", "Open App",
                    "Open an application by package name.", Common.SafetyLevel.LEVEL_1_SAFE_ACT),
                buildCapability("android.press_home", "Press Home",
                    "Press the home button.", Common.SafetyLevel.LEVEL_1_SAFE_ACT),
            )

            for (cap in caps) {
                val capRequest = AiServer.RegisterCapabilityRequest.newBuilder()
                    .setCapability(cap)
                    .build()
                stub!!.registerCapability(capRequest)
            }

            Log.i(TAG, "Registered ${caps.size} capabilities with AEGIS Core")
            true
        } catch (e: StatusRuntimeException) {
            Log.e(TAG, "gRPC error registering capabilities", e)
            false
        } catch (e: Exception) {
            Log.e(TAG, "Error registering capabilities", e)
            false
        }
    }

    suspend fun pushNotification(
        packageName: String,
        appName: String,
        title: String,
        text: String,
        postedMs: Long,
        isOngoing: Boolean,
        isClearable: Boolean,
    ): Boolean = withContext(Dispatchers.IO) {
        if (!connected || stub == null) {
            Log.w(TAG, "Not connected - cannot push notification")
            return@withContext false
        }

        try {
            val payload = """{"app_name":"$appName","title":"$title","text":"$text","package_name":"$packageName"}"""

            val eventObj = event {
                eventId = "evt_${java.util.UUID.randomUUID().toString().take(8)}"
                eventType = "android.notification_received"
                sourceServerType = Common.ServerType.SERVER_TYPE_ANDROID
                sourceServerId = "android-server-main"
                timestampMs = System.currentTimeMillis()
                payloadJson = payload
                severity = Common.EventSeverity.EVENT_SEVERITY_MODERATE
                priority = Common.EventPriority.EVENT_PRIORITY_NORMAL
                dedupeKey = "android.notification:$packageName:$title"
            }

            val request = AiServer.PushEventRequest.newBuilder()
                .setEvent(eventObj)
                .build()

            val response = stub!!.pushEvent(request)
            if (response.status.code != 0) {
                Log.e(TAG, "Failed to push event: ${response.status.message}")
                return@withContext false
            }

            Log.d(TAG, "Pushed notification: pkg=$packageName title=$title")
            true
        } catch (e: StatusRuntimeException) {
            Log.e(TAG, "gRPC error pushing notification", e)
            false
        } catch (e: Exception) {
            Log.e(TAG, "Error pushing notification", e)
            false
        }
    }

    suspend fun pushDeviceState(
        batteryLevel: Int,
        screenOn: Boolean,
    ): Boolean = withContext(Dispatchers.IO) {
        if (!connected || stub == null) return@withContext false

        try {
            val payload = """{"battery_level":$batteryLevel,"screen_on":$screenOn}"""

            val eventObj = event {
                eventId = "evt_${java.util.UUID.randomUUID().toString().take(8)}"
                eventType = "android.device_state"
                sourceServerType = Common.ServerType.SERVER_TYPE_ANDROID
                sourceServerId = "android-server-main"
                timestampMs = System.currentTimeMillis()
                payloadJson = payload
                severity = Common.EventSeverity.EVENT_SEVERITY_INFO
                priority = Common.EventPriority.EVENT_PRIORITY_BACKGROUND
                dedupeKey = "android.device_state:$batteryLevel:$screenOn"
            }

            val request = AiServer.PushEventRequest.newBuilder()
                .setEvent(eventObj)
                .build()

            stub!!.pushEvent(request)
            Log.d(TAG, "Pushed device state: battery=$batteryLevel screen=$screenOn")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Error pushing device state", e)
            false
        }
    }

    fun isConnected(): Boolean = connected

    private fun buildCapability(
        id: String, name: String, description: String, safetyLevel: Common.SafetyLevel
    ): Common.Capability {
        return capability {
            this.id = id
            this.name = name
            this.description = description
            this.serverType = Common.ServerType.SERVER_TYPE_ANDROID
            this.safetyLevel = safetyLevel
            tags.addAll(listOf("observe", "read_only"))
        }
    }
}
