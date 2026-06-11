package com.aegis.android.grpc

import android.util.Log
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import io.grpc.StatusRuntimeException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.concurrent.TimeUnit

/**
 * gRPC client for communicating with AEGIS Core (AI Server).
 *
 * Connects to the AIServer service defined in protos/aegis/ai_server.proto
 * for capability registration and event push.
 *
 * Generated stubs are created by Gradle's protobuf plugin from the proto files
 * in app/src/main/proto/aegis/.
 */
class AegisGrpcClient private constructor(
    private val host: String,
    private val port: Int,
) {
    companion object {
        private const val TAG = "AegisGrpcClient"
        private const val DEFAULT_HOST = "10.0.2.2" // Android emulator → host machine
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
    private var connected = false

    // Generated gRPC stubs (will be available after Gradle generates from proto)
    // private var aiServerStub: AIServerGrpc.AIServerCoroutineStub? = null

    /**
     * Connect to AEGIS Core.
     */
    suspend fun connect(): Boolean = withContext(Dispatchers.IO) {
        try {
            channel = ManagedChannelBuilder
                .forAddress(host, port)
                .usePlaintext() // TODO: Add TLS for production
                .keepAliveTime(30, TimeUnit.SECONDS)
                .build()

            // Initialize generated stub
            // aiServerStub = AIServerGrpc.AIServerCoroutineStub(channel!!)

            connected = true
            Log.i(TAG, "Connected to AEGIS Core at $host:$port")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to connect to AEGIS Core", e)
            connected = false
            false
        }
    }

    /**
     * Disconnect from AEGIS Core.
     */
    fun disconnect() {
        try {
            channel?.shutdown()?.awaitTermination(5, TimeUnit.SECONDS)
        } catch (e: Exception) {
            Log.e(TAG, "Error disconnecting", e)
        } finally {
            channel = null
            connected = false
        }
    }

    /**
     * Register this Android server and its capabilities with AEGIS Core.
     *
     * Calls AIServer.RegisterServer and AIServer.RegisterCapability RPCs.
     */
    suspend fun registerCapabilities(): Boolean = withContext(Dispatchers.IO) {
        if (!connected) {
            Log.w(TAG, "Not connected — cannot register capabilities")
            return@withContext false
        }

        try {
            // TODO: Uncomment when generated stubs are available
            // val serverInfo = ServerInfo.newBuilder()
            //     .setServerId("android-server-main")
            //     .setServerType(ServerType.SERVER_TYPE_ANDROID)
            //     .setVersion("0.1.0")
            //     .setServerStatus(ServerStatus.SERVER_STATUS_ONLINE)
            //     .addAllCapabilityIds(listOf(
            //         "android.get_notifications",
            //         "android.get_current_app",
            //         "android.get_device_info",
            //     ))
            //     .setHost(host)
            //     .setPort(port)
            //     .setStartedAtMs(System.currentTimeMillis())
            //     .build()
            //
            // val registerRequest = RegisterServerRequest.newBuilder()
            //     .setServerInfo(serverInfo)
            //     .build()
            //
            // val response = aiServerStub!!.registerServer(registerRequest)
            // if (response.status.code != 0) {
            //     Log.e(TAG, "Failed to register server: ${response.status.message}")
            //     return@withContext false
            // }
            //
            // // Register each capability
            // val capabilities = listOf(
            //     buildCapability("android.get_notifications", "Get Notifications",
            //         "Retrieve current status bar notifications.", SafetyLevel.LEVEL_0_READ),
            //     buildCapability("android.get_current_app", "Get Current App",
            //         "Return the package name and activity of the foreground app.", SafetyLevel.LEVEL_0_READ),
            //     buildCapability("android.get_device_info", "Get Device Info",
            //         "Return device model, Android version, battery level.", SafetyLevel.LEVEL_0_READ),
            // )
            //
            // for (cap in capabilities) {
            //     val capRequest = RegisterCapabilityRequest.newBuilder()
            //         .setCapability(cap)
            //         .build()
            //     aiServerStub!!.registerCapability(capRequest)
            // }

            Log.i(TAG, "Registered capabilities with AEGIS Core (stub)")
            true
        } catch (e: StatusRuntimeException) {
            Log.e(TAG, "gRPC error registering capabilities", e)
            false
        } catch (e: Exception) {
            Log.e(TAG, "Error registering capabilities", e)
            false
        }
    }

    /**
     * Push a notification event to AEGIS Core.
     *
     * Calls AIServer.PushEvent RPC.
     */
    suspend fun pushNotification(
        packageName: String,
        appName: String,
        title: String,
        text: String,
        postedMs: Long,
        isOngoing: Boolean,
        isClearable: Boolean,
    ): Boolean = withContext(Dispatchers.IO) {
        if (!connected) {
            Log.w(TAG, "Not connected — cannot push notification")
            return@withContext false
        }

        try {
            // TODO: Uncomment when generated stubs are available
            // val payload = """{"app_name":"$appName","title":"$title","text":"$text","package_name":"$packageName"}"""
            //
            // val event = Event.newBuilder()
            //     .setEventId("evt_${java.util.UUID.randomUUID().toString().take(8)}")
            //     .setEventType("android.notification_received")
            //     .setSourceServerType(ServerType.SERVER_TYPE_ANDROID)
            //     .setSourceServerId("android-server-main")
            //     .setTimestampMs(System.currentTimeMillis())
            //     .setPayloadJson(payload)
            //     .setSeverity(EventSeverity.EVENT_SEVERITY_MODERATE)
            //     .setPriority(EventPriority.EVENT_PRIORITY_NORMAL)
            //     .setDedupeKey("android.notification:$packageName:$title")
            //     .build()
            //
            // val request = PushEventRequest.newBuilder()
            //     .setEvent(event)
            //     .build()
            //
            // val response = aiServerStub!!.pushEvent(request)
            // if (response.status.code != 0) {
            //     Log.e(TAG, "Failed to push event: ${response.status.message}")
            //     return@withContext false
            // }

            Log.d(TAG, "Pushed notification: pkg=$packageName title=$title (stub)")
            true
        } catch (e: StatusRuntimeException) {
            Log.e(TAG, "gRPC error pushing notification", e)
            false
        } catch (e: Exception) {
            Log.e(TAG, "Error pushing notification", e)
            false
        }
    }

    /**
     * Push device state to AEGIS Core.
     */
    suspend fun pushDeviceState(
        batteryLevel: Int,
        screenOn: Boolean,
    ): Boolean = withContext(Dispatchers.IO) {
        if (!connected) return@withContext false

        try {
            // TODO: Implement with generated stubs
            Log.d(TAG, "Pushed device state: battery=$batteryLevel screen=$screenOn (stub)")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Error pushing device state", e)
            false
        }
    }

    fun isConnected(): Boolean = connected

    // private fun buildCapability(
    //     id: String, name: String, description: String, safetyLevel: SafetyLevel
    // ): Capability {
    //     return Capability.newBuilder()
    //         .setId(id)
    //         .setName(name)
    //         .setDescription(description)
    //         .setServerType(ServerType.SERVER_TYPE_ANDROID)
    //         .setServerId("android-server-main")
    //         .setSafetyLevel(safetyLevel)
    //         .addTags("observe")
    //         .addTags("read_only")
    //         .build()
    // }
}
