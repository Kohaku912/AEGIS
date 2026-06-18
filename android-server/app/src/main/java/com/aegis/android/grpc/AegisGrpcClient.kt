package com.aegis.android.grpc

import android.content.Context
import android.os.Build
import android.util.Log
import aegis.AIServerGrpcKt
import aegis.AndroidServerOuterClass
import aegis.Common
import com.aegis.android.AegisConfig
import com.aegis.android.AegisConnectionConfig
import com.aegis.android.overlay.OverlayController
import com.aegis.android.provider.DeviceProvider
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.UUID
import java.util.concurrent.TimeUnit

class AegisGrpcClient private constructor(
    private val context: Context,
    private var config: AegisConnectionConfig,
) {
    companion object {
        private const val TAG = "AegisGrpcClient"
        private const val HEARTBEAT_INTERVAL_MS = 30_000L
        private const val APP_VERSION = "0.2.0"

        @Volatile
        private var instance: AegisGrpcClient? = null

        fun getInstance(context: Context): AegisGrpcClient {
            val appContext = context.applicationContext
            val loaded = AegisConfig.load(appContext)
            return synchronized(this) {
                val current = instance
                if (current != null && current.config.host == loaded.host && current.config.port == loaded.port &&
                    current.config.pairingToken == loaded.pairingToken
                ) {
                    current
                } else {
                    current?.disconnect()
                    AegisGrpcClient(appContext, loaded).also { instance = it }
                }
            }
        }

        fun current(): AegisGrpcClient? = instance
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val deviceProvider = DeviceProvider(context)
    private val overlayController = OverlayController(context)
    private val dispatcher = AndroidCapabilityDispatcher(context, overlayController) { decision ->
        sendApprovalDecision(decision)
    }

    private var channel: ManagedChannel? = null
    private var stub: AIServerGrpcKt.AIServerCoroutineStub? = null
    private var outbound: Channel<AndroidServerOuterClass.AndroidClientMessage>? = null
    private var streamJob: Job? = null
    private var heartbeatJob: Job? = null
    private var connected = false
    private var lastHeartbeatMs = 0L
    private var connectionId = "android_${UUID.randomUUID().toString().replace("-", "").take(10)}"

    suspend fun connect(): Boolean = withContext(Dispatchers.IO) {
        if (config.pairingToken.isBlank()) {
            Log.w(TAG, "Pairing token is required")
            connected = false
            return@withContext false
        }
        disconnect()
        try {
            channel = ManagedChannelBuilder
                .forAddress(config.host, config.port)
                .usePlaintext()
                .keepAliveTime(30, TimeUnit.SECONDS)
                .build()
            stub = AIServerGrpcKt.AIServerCoroutineStub(channel!!)

            val healthResponse = stub!!.healthCheck(Common.HealthCheckRequest.getDefaultInstance())
            if (healthResponse.status.code != 0) {
                Log.e(TAG, "Health check failed: ${healthResponse.status.message}")
                connected = false
                return@withContext false
            }

            startReverseStream()
            connected = true
            Log.i(TAG, "Reverse stream started for AEGIS Core at ${config.host}:${config.port}")
            true
        } catch (exc: Exception) {
            Log.e(TAG, "Failed to connect to AEGIS Core", exc)
            connected = false
            false
        }
    }

    fun disconnect() {
        connected = false
        heartbeatJob?.cancel()
        streamJob?.cancel()
        outbound?.close()
        heartbeatJob = null
        streamJob = null
        outbound = null
        try {
            channel?.shutdown()?.awaitTermination(3, TimeUnit.SECONDS)
        } catch (exc: Exception) {
            Log.e(TAG, "Error disconnecting", exc)
        } finally {
            channel = null
            stub = null
        }
    }

    fun isConnected(): Boolean = connected

    fun lastHeartbeatMs(): Long = lastHeartbeatMs

    fun currentConfig(): AegisConnectionConfig = config

    suspend fun registerCapabilities(): Boolean = true

    suspend fun pushNotification(
        packageName: String,
        appName: String,
        title: String,
        text: String,
        postedMs: Long,
        isOngoing: Boolean,
        isClearable: Boolean,
    ): Boolean {
        val payload = """{"package_name":${jsonString(packageName)},"app_name":${jsonString(appName)},"title":${jsonString(title)},"text":${jsonString(text)},"posted_ms":$postedMs,"is_ongoing":$isOngoing,"is_clearable":$isClearable}"""
        return sendEvent(
            eventType = "android.notification.posted",
            payloadJson = payload,
            dedupeKey = "android.notification.posted:$packageName:$postedMs",
        )
    }

    suspend fun pushDeviceState(batteryLevel: Int, screenOn: Boolean): Boolean {
        sendHeartbeat()
        val payload = """{"battery_level":$batteryLevel,"screen_on":$screenOn,"locked":${deviceProvider.isLocked()}}"""
        return sendEvent("android.heartbeat", payload, "android.heartbeat:${config.deviceId}")
    }

    fun pushForegroundApp(packageName: String) {
        scope.launch {
            val payload = """{"package_name":${jsonString(packageName)}}"""
            sendEvent(
                eventType = "android.foreground_app.changed",
                payloadJson = payload,
                dedupeKey = "android.foreground_app.changed:${config.deviceId}:$packageName",
            )
        }
    }

    fun pushPermissionChanged() {
        scope.launch {
            sendEvent(
                eventType = "android.permission.changed",
                payloadJson = dispatcher.permissionSnapshotJson().toString(),
                dedupeKey = "android.permission.changed:${config.deviceId}",
            )
        }
    }

    private suspend fun startReverseStream() {
        val localOutbound = Channel<AndroidServerOuterClass.AndroidClientMessage>(Channel.BUFFERED)
        outbound = localOutbound
        localOutbound.send(registerMessage())

        val currentStub = stub ?: error("stub missing")
        streamJob = scope.launch {
            try {
                currentStub.connect(localOutbound.receiveAsFlow()).collect { command ->
                    handleServerCommand(command)
                }
            } catch (exc: Exception) {
                Log.e(TAG, "Reverse stream closed", exc)
            } finally {
                connected = false
            }
        }
        heartbeatJob = scope.launch {
            while (isActive) {
                delay(HEARTBEAT_INTERVAL_MS)
                sendHeartbeat()
            }
        }
        sendEvent(
            eventType = "android.connected",
            payloadJson = """{"connection_mode":"reverse_stream"}""",
            dedupeKey = "android.connected:${config.deviceId}:$connectionId",
        )
        sendHeartbeat()
        pushPermissionChanged()
    }

    private fun handleServerCommand(command: AndroidServerOuterClass.AndroidServerCommand) {
        when (command.kindCase) {
            AndroidServerOuterClass.AndroidServerCommand.KindCase.ACK -> {
                connectionId = command.ack.connectionId.ifBlank { connectionId }
                Log.i(TAG, "Stream acknowledged: $connectionId")
            }
            AndroidServerOuterClass.AndroidServerCommand.KindCase.HEARTBEAT -> {
                lastHeartbeatMs = command.heartbeat.timestampMs
            }
            AndroidServerOuterClass.AndroidServerCommand.KindCase.INVOKE -> {
                Log.i(TAG, "Invoke command received: ${command.invoke.capabilityId}")
                scope.launch { handleInvoke(command.invoke) }
            }
            AndroidServerOuterClass.AndroidServerCommand.KindCase.APPROVAL_REQUEST -> {
                Log.i(TAG, "Approval command received: ${command.approvalRequest.approvalId}")
                handleApprovalCommand(command.approvalRequest)
            }
            AndroidServerOuterClass.AndroidServerCommand.KindCase.STOP -> {
                Log.w(TAG, "Server requested stream stop: ${command.stop.reason}")
                disconnect()
            }
            else -> Unit
        }
    }

    private suspend fun handleInvoke(command: AndroidServerOuterClass.AndroidInvokeCommand) {
        val result = try {
            dispatcher.dispatch(command)
        } catch (exc: Exception) {
            Log.e(TAG, "Command failed: ${command.capabilityId}", exc)
            AndroidCapabilityDispatcher.DispatchResult(
                Common.Status.newBuilder().setCode(1).setMessage("ANDROID_COMMAND_FAILED: ${exc.message}").build(),
                """{"code":"ANDROID_COMMAND_FAILED","error":${jsonString(exc.message ?: "Command failed")}}""",
            )
        }
        val message = AndroidServerOuterClass.AndroidClientMessage.newBuilder()
            .setCommandResult(
                AndroidServerOuterClass.AndroidCommandResult.newBuilder()
                    .setAuth(auth())
                    .setCommandId(command.commandId)
                    .setCapabilityId(command.capabilityId)
                    .setStatus(result.status)
                    .setResultJson(result.resultJson)
                    .build(),
            )
            .build()
        outbound?.send(message)
    }

    private fun handleApprovalCommand(command: AndroidServerOuterClass.AndroidApprovalCommand) {
        overlayController.showApproval(
            approvalId = command.approvalId,
            title = command.title.ifBlank { "AEGIS approval" },
            body = command.body.ifBlank { command.summaryJson },
        ) { decision ->
            sendApprovalDecision(decision)
        }
    }

    private fun sendApprovalDecision(decision: OverlayController.ApprovalAction) {
        scope.launch {
            val message = AndroidServerOuterClass.AndroidClientMessage.newBuilder()
                .setApprovalDecision(
                    AndroidServerOuterClass.AndroidApprovalDecision.newBuilder()
                        .setAuth(auth())
                        .setApprovalId(decision.approvalId)
                        .setApproved(decision.approved)
                        .setRejected(decision.rejected)
                        .setGlobalReject(decision.globalReject)
                        .setSurfaceId("android_overlay")
                        .setUser(config.deviceId)
                        .setReason(decision.reason)
                        .build(),
                )
                .build()
            outbound?.send(message)
        }
    }

    private suspend fun sendHeartbeat(): Boolean {
        val device = deviceProvider.getDeviceInfo()
        val message = AndroidServerOuterClass.AndroidClientMessage.newBuilder()
            .setHeartbeat(
                AndroidServerOuterClass.AndroidHeartbeat.newBuilder()
                    .setAuth(auth())
                    .setTimestampMs(System.currentTimeMillis())
                    .setBatteryLevel(device.batteryLevel)
                    .setScreenOn(device.screenOn)
                    .setLocked(device.locked)
                    .build(),
            )
            .build()
        lastHeartbeatMs = System.currentTimeMillis()
        return runCatching {
            outbound?.send(message)
            true
        }.getOrDefault(false)
    }

    private suspend fun sendEvent(eventType: String, payloadJson: String, dedupeKey: String): Boolean {
        val event = Common.Event.newBuilder()
            .setEventId("evt_${UUID.randomUUID().toString().replace("-", "").take(12)}")
            .setEventType(eventType)
            .setSourceServerType(Common.ServerType.SERVER_TYPE_ANDROID)
            .setSourceServerId("android-server")
            .setTimestampMs(System.currentTimeMillis())
            .setPayloadJson(payloadJson)
            .setSeverity(Common.EventSeverity.EVENT_SEVERITY_INFO)
            .setPriority(Common.EventPriority.EVENT_PRIORITY_NORMAL)
            .setDedupeKey(dedupeKey)
            .putAttributes("device_id", config.deviceId)
            .putAttributes("connection_id", connectionId)
            .build()
        val message = AndroidServerOuterClass.AndroidClientMessage.newBuilder()
            .setEvent(AndroidServerOuterClass.AndroidEventEnvelope.newBuilder().setAuth(auth()).setEvent(event).build())
            .build()
        return runCatching {
            outbound?.send(message)
            true
        }.getOrDefault(false)
    }

    private fun registerMessage(): AndroidServerOuterClass.AndroidClientMessage {
        val device = deviceProvider.getDeviceInfo()
        return AndroidServerOuterClass.AndroidClientMessage.newBuilder()
            .setRegister(
                AndroidServerOuterClass.AndroidRegister.newBuilder()
                    .setAuth(auth())
                    .setDeviceModel(device.model)
                    .setManufacturer(device.manufacturer)
                    .setAndroidVersion(device.androidVersion)
                    .setAppVersion(APP_VERSION)
                    .addAllCapabilityIds(AndroidCapabilityDispatcher.CAPABILITY_IDS)
                    .putMetadata("sdk_version", Build.VERSION.SDK_INT.toString())
                    .putMetadata("screen_on", device.screenOn.toString())
                    .build(),
            )
            .build()
    }

    private fun auth(): AndroidServerOuterClass.AndroidAuth {
        return AndroidServerOuterClass.AndroidAuth.newBuilder()
            .setDeviceId(config.deviceId)
            .setPairingToken(config.pairingToken)
            .setConnectionId(connectionId)
            .build()
    }

    private fun jsonString(value: String): String {
        return "\"" + value
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", "\\n")
            .replace("\r", "\\r") + "\""
    }
}
