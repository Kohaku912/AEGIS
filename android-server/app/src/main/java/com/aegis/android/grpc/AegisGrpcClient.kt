package com.aegis.android.grpc

import android.content.Context
import android.os.Build
import android.util.Log
import aegis.AIServerGrpcKt
import aegis.AiServer
import aegis.AndroidServerOuterClass
import aegis.Common
import com.aegis.android.AegisConfig
import com.aegis.android.AegisConnectionConfig
import com.aegis.android.overlay.OverlayController
import com.aegis.android.provider.DeviceProvider
import com.aegis.android.ui.model.UiServerSummary
import com.aegis.android.ui.model.UiOverviewSnapshot
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import io.grpc.Status
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.security.MessageDigest
import java.util.UUID
import java.util.concurrent.TimeUnit

data class AegisConnectionState(
    val connected: Boolean = false,
    val connecting: Boolean = false,
    val lastHeartbeatMs: Long = 0L,
    val lastError: String = "",
    val nextRetryMs: Long = 0L,
    val host: String = "",
    val port: Int = 0,
    val coreVersion: String = "",
    val chatRpcAvailable: Boolean = false,
)

data class ChatReply(
    val ok: Boolean,
    val conversationId: String,
    val response: String,
    val approvalNeeded: Boolean = false,
    val approvalId: String = "",
    val error: String = "",
)

data class ApprovalItem(
    val approvalId: String,
    val capabilityId: String,
    val summary: String,
    val risk: String,
    val requestedAction: String = "",
    val reason: String = "",
    val preview: String = "",
    val target: String = "",
    val taskId: String = "",
    val status: String = "",
    val createdAtMs: Long = 0L,
    val expiresAtMs: Long = 0L,
)

data class ToolReply(
    val ok: Boolean,
    val output: String = "",
    val error: String = "",
)

data class MobileServerStatus(
    val serverId: String,
    val label: String,
    val status: String,
    val mode: String = "",
    val detail: String = "",
)

data class MobileChatMessage(
    val messageId: String,
    val role: String,
    val text: String,
    val timestampMs: Long,
    val image: String = "",
    val conversationId: String = "",
    val source: String = "",
)

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
    private var dashboardRefreshJob: Job? = null
    private var connected = false
    private var lastHeartbeatMs = 0L
    private var connectionId = "android_${UUID.randomUUID().toString().replace("-", "").take(10)}"
    private val _state = MutableStateFlow(
        AegisConnectionState(host = config.host, port = config.port)
    )
    val state: StateFlow<AegisConnectionState> = _state.asStateFlow()
    private val _serverStatuses = MutableStateFlow<List<MobileServerStatus>>(emptyList())
    val serverStatuses: StateFlow<List<MobileServerStatus>> = _serverStatuses.asStateFlow()
    private val _chatMessages = MutableStateFlow<List<MobileChatMessage>>(emptyList())
    val chatMessages: StateFlow<List<MobileChatMessage>> = _chatMessages.asStateFlow()
    private val _uiOverview = MutableStateFlow(UiOverviewSnapshot())
    val uiOverview: StateFlow<UiOverviewSnapshot> = _uiOverview.asStateFlow()

    suspend fun connect(): Boolean = withContext(Dispatchers.IO) {
        if (config.pairingToken.isBlank()) {
            Log.w(TAG, "Pairing token is required")
            connected = false
            updateState(connected = false, connecting = false, lastError = "Pairing token is required")
            return@withContext false
        }
        updateState(connecting = true, lastError = "")
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
                updateState(connected = false, connecting = false, lastError = healthResponse.status.message)
                return@withContext false
            }

            val coreVersion = healthResponse.version
            val chatRpcAvailable = supportsSendChat(coreVersion)
            startReverseStream()
            connected = true
            updateState(
                connected = true,
                connecting = false,
                lastError = "",
                nextRetryMs = 0L,
                coreVersion = coreVersion,
                chatRpcAvailable = chatRpcAvailable,
            )
            refreshMobileDashboardState()
            refreshUiOverview()
            startMobileDashboardRefresh()
            Log.i(TAG, "Reverse stream started for AEGIS Core at ${config.host}:${config.port}")
            true
        } catch (exc: Exception) {
            Log.e(TAG, "Failed to connect to AEGIS Core", exc)
            connected = false
            updateState(connected = false, connecting = false, lastError = exc.message ?: "Connection failed")
            false
        }
    }

    fun disconnect() {
        connected = false
        updateState(connected = false, connecting = false)
        heartbeatJob?.cancel()
        streamJob?.cancel()
        dashboardRefreshJob?.cancel()
        outbound?.close()
        heartbeatJob = null
        streamJob = null
        dashboardRefreshJob = null
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

    fun setNextRetry(timestampMs: Long) {
        updateState(nextRetryMs = timestampMs)
    }

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
        val payload = """{"package_name":${jsonString(packageName)},"app_name":${jsonString(appName)},"title_hash":${jsonString(sha256(title))},"text_hash":${jsonString(sha256(text))},"posted_ms":$postedMs,"is_ongoing":$isOngoing,"is_clearable":$isClearable,"metadata_only":true}"""
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
            val payload = """{"package_name":${jsonString(packageName)},"app_name":${jsonString(appName(packageName))}}"""
            sendEvent(
                eventType = "android.foreground_app.changed",
                payloadJson = payload,
                dedupeKey = "android.foreground_app.changed:${config.deviceId}:$packageName",
            )
        }
    }

    fun pushUserActivity(payloadJson: String) {
        scope.launch {
            sendEvent(
                eventType = "android.user_activity.changed",
                payloadJson = payloadJson,
                dedupeKey = "android.user_activity.changed:${config.deviceId}:${payloadJson.hashCode()}",
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

    suspend fun sendChat(text: String, conversationId: String = ""): ChatReply = withContext(Dispatchers.IO) {
        val currentStub = stub ?: return@withContext ChatReply(
            ok = false,
            conversationId = conversationId,
            response = "",
            error = "AEGIS Core is not connected",
        )
        try {
            val response = currentStub.sendChat(
                AiServer.ChatRequest.newBuilder()
                    .setConversationId(conversationId)
                    .setText(text)
                    .setDeviceId(config.deviceId)
                    .setAuth(auth())
                    .putContext("surface", "android_app")
                    .build()
            )
            ChatReply(
                ok = response.status.code == 0,
                conversationId = response.conversationId,
                response = response.response,
                approvalNeeded = response.approvalNeeded,
                approvalId = response.approvalId,
                error = if (response.status.code == 0) "" else response.status.message,
            ).also {
                if (it.ok) {
                    refreshMobileDashboardState()
                    refreshUiOverview()
                }
            }
        } catch (exc: Exception) {
            Log.e(TAG, "Chat request failed", exc)
            val errorMessage = chatErrorMessage(exc)
            updateState(
                lastError = errorMessage,
                chatRpcAvailable = if (isMethodNotFound(exc)) false else _state.value.chatRpcAvailable,
            )
            ChatReply(
                ok = false,
                conversationId = conversationId,
                response = "",
                error = errorMessage,
            )
        }
    }

    suspend fun refreshMobileDashboardState(historyLimit: Int = 80): Boolean = withContext(Dispatchers.IO) {
        val currentStub = stub ?: return@withContext false
        try {
            val response = currentStub.getMobileDashboardState(
                AiServer.MobileDashboardStateRequest.newBuilder()
                    .setDeviceId(config.deviceId)
                    .setHistoryLimit(historyLimit)
                    .setAuth(auth())
                    .build()
            )
            if (response.status.code != 0) {
                updateState(lastError = response.status.message)
                return@withContext false
            }
            _serverStatuses.value = response.serverStatusesList.map {
                MobileServerStatus(
                    serverId = it.serverId,
                    label = it.label,
                    status = it.status,
                    mode = it.mode,
                    detail = it.detail,
                )
            }
            mergeChatMessages(
                response.chatHistoryList.map {
                    MobileChatMessage(
                        messageId = it.messageId,
                        role = it.role,
                        text = it.text,
                        timestampMs = it.timestampMs,
                        image = it.image,
                        conversationId = it.conversationId,
                        source = it.source,
                    )
                }
            )
            true
        } catch (exc: Exception) {
            Log.e(TAG, "Mobile dashboard state refresh failed", exc)
            val message = if (isMethodNotFound(exc)) {
                "AEGIS Core gRPC is older than this Android app. Restart AEGIS Core with the latest code, then reconnect. (GetMobileDashboardState method not found)"
            } else {
                exc.message ?: "Mobile dashboard state refresh failed"
            }
            updateState(
                lastError = message,
                chatRpcAvailable = if (isMethodNotFound(exc)) false else _state.value.chatRpcAvailable,
            )
            false
        }
    }

    suspend fun refreshUiOverview(): Boolean = withContext(Dispatchers.IO) {
        val currentStub = stub ?: return@withContext false
        try {
            val response = currentStub.getUiOverview(
                AiServer.UiOverviewRequest.newBuilder()
                    .setSurfaceId(config.deviceId)
                    .setAuth(auth())
                    .build()
            )
            if (response.status.code != 0) {
                updateState(lastError = response.status.message)
                return@withContext false
            }
            _uiOverview.value = parseUiOverview(response.overviewJson, response.generatedAtMs)
            true
        } catch (exc: Exception) {
            Log.e(TAG, "UI overview refresh failed", exc)
            updateState(lastError = exc.message ?: "UI overview refresh failed")
            false
        }
    }

    suspend fun listPendingApprovals(): List<ApprovalItem> = withContext(Dispatchers.IO) {
        val currentStub = stub ?: return@withContext emptyList()
        try {
            val response = currentStub.listPendingApprovals(
                AiServer.ListPendingApprovalsRequest.newBuilder()
                    .setServerId("android-server")
                    .setAuth(auth())
                    .build()
            )
            response.approvalsList.map {
                val summary = listOf(
                    it.humanReadableSummary,
                    it.riskExplanation.takeIf { reason -> reason.isNotBlank() }?.let { reason -> "Reason: $reason" } ?: "",
                    it.payloadPreview.takeIf { preview -> preview.isNotBlank() }?.let { preview -> "Details: $preview" } ?: "",
                ).filter { part -> part.isNotBlank() }.joinToString("\n")
                ApprovalItem(
                    approvalId = it.approvalId,
                    capabilityId = it.capabilityId,
                    summary = summary.ifBlank { it.requestedAction.ifBlank { it.approvalId } },
                    risk = it.riskExplanation,
                    requestedAction = it.requestedAction,
                    reason = it.riskExplanation,
                    preview = it.payloadPreview,
                    target = it.toolName,
                    status = it.status.name,
                    createdAtMs = it.createdAtMs,
                    expiresAtMs = it.expiresAtMs,
                )
            }
        } catch (exc: Exception) {
            Log.e(TAG, "List approvals failed", exc)
            updateState(lastError = exc.message ?: "List approvals failed")
            emptyList()
        }
    }

    suspend fun resolveApproval(approvalId: String, approved: Boolean): Boolean = withContext(Dispatchers.IO) {
        val currentStub = stub ?: return@withContext false
        try {
            val request = AiServer.ResolveApprovalRequest.newBuilder()
                .setApprovalId(approvalId)
                .setSurfaceId("android_app")
                .setUser(config.deviceId)
                .setAuth(auth())
            if (approved) {
                request.setApprovedType(Common.ApprovalType.APPROVAL_TYPE_ONE_TIME)
            } else {
                request.setRejected(true)
            }
            val response = currentStub.resolveApproval(request.build())
            response.status.code == 0
        } catch (exc: Exception) {
            Log.e(TAG, "Resolve approval failed", exc)
            updateState(lastError = exc.message ?: "Resolve approval failed")
            false
        }
    }

    suspend fun invokeTool(capabilityId: String, paramsJson: String = "{}"): ToolReply = withContext(Dispatchers.IO) {
        val currentStub = stub ?: return@withContext ToolReply(false, error = "AEGIS Core is not connected")
        try {
            val response = currentStub.invokeTool(
                Common.ToolInvocationRequest.newBuilder()
                    .setCapabilityId(capabilityId)
                    .setInvocationId("android_${UUID.randomUUID().toString().replace("-", "").take(10)}")
                    .setCaller("android_app")
                    .setParamsJson(paramsJson)
                    .build()
            )
            ToolReply(
                ok = response.status.code == 0,
                output = response.outputJson,
                error = response.error.ifBlank { response.status.message },
            )
        } catch (exc: Exception) {
            Log.e(TAG, "Invoke tool failed", exc)
            updateState(lastError = exc.message ?: "Invoke tool failed")
            ToolReply(false, error = exc.message ?: "Invoke tool failed")
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
                updateState(lastError = exc.message ?: "Reverse stream closed")
            } finally {
                connected = false
                updateState(connected = false, connecting = false)
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
            AndroidServerOuterClass.AndroidServerCommand.KindCase.CHAT_UPDATE -> {
                mergeChatMessages(
                    command.chatUpdate.messagesList.map {
                        MobileChatMessage(
                            messageId = it.messageId,
                            role = it.role,
                            text = it.text,
                            timestampMs = it.timestampMs,
                            image = it.image,
                            conversationId = it.conversationId,
                            source = it.source,
                        )
                    }
                )
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
            body = command.body.ifBlank { approvalBodyFromSummaryJson(command.summaryJson) },
        ) { decision ->
            sendApprovalDecision(decision)
        }
    }

    private fun approvalBodyFromSummaryJson(summaryJson: String): String {
        if (summaryJson.isBlank()) return "Approval is required."
        return runCatching {
            val obj = JSONObject(summaryJson)
            listOf(
                obj.optString("body"),
                obj.optString("user_facing_summary"),
                obj.optString("approval_reason").takeIf { it.isNotBlank() }?.let { "Reason: $it" } ?: "",
                obj.optString("arguments_summary").takeIf { it.isNotBlank() }?.let { "Details: $it" } ?: "",
                obj.optString("risk_level").takeIf { it.isNotBlank() }?.let { "Risk: $it" } ?: "",
                obj.optString("approval_id").takeIf { it.isNotBlank() }?.let { "ID: $it" } ?: "",
            ).filter { it.isNotBlank() }.joinToString("\n").ifBlank { summaryJson }
        }.getOrDefault(summaryJson)
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
        updateState(lastHeartbeatMs = lastHeartbeatMs)
        return runCatching {
            outbound?.send(message)
            true
        }.getOrElse {
            updateState(connected = false, lastError = it.message ?: "Heartbeat failed")
            false
        }
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
        }.getOrElse {
            updateState(connected = false, lastError = it.message ?: "Event send failed")
            false
        }
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

    private fun appName(packageName: String): String {
        if (packageName.isBlank()) return ""
        return runCatching {
            val info = context.packageManager.getApplicationInfo(packageName, 0)
            context.packageManager.getApplicationLabel(info).toString().takeUnless { it.isBlank() || it == packageName }
                ?: fallbackAppName(packageName)
        }.getOrElse { fallbackAppName(packageName) }
    }

    private fun fallbackAppName(packageName: String): String = when (packageName) {
        "com.google.android.youtube" -> "YouTube"
        "com.android.chrome" -> "Chrome"
        "com.google.android.googlequicksearchbox" -> "Google"
        "com.android.systemui" -> "System UI"
        else -> packageName
    }

    private fun sha256(value: String): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(value.toByteArray(Charsets.UTF_8))
        return digest.joinToString("") { "%02x".format(it) }
    }

    private fun supportsSendChat(version: String): Boolean {
        val normalized = version.lowercase()
        return normalized.contains("sendchat") || normalized.contains("chat-v1")
    }

    private fun isMethodNotFound(exc: Throwable): Boolean {
        val status = Status.fromThrowable(exc)
        val rawMessage = listOfNotNull(exc.message, status.description).joinToString(" ").lowercase()
        return status.code == Status.Code.UNIMPLEMENTED ||
            ("method" in rawMessage && "not found" in rawMessage) ||
            ("sendchat" in rawMessage && ("not found" in rawMessage || "unimplemented" in rawMessage))
    }

    private fun chatErrorMessage(exc: Throwable): String {
        if (isMethodNotFound(exc)) {
            return "AEGIS Core gRPC is older than this Android app. Restart AEGIS Core with the latest code, then reconnect. (SendChat method not found)"
        }
        val status = Status.fromThrowable(exc)
        return exc.message ?: status.description ?: "Chat request failed"
    }

    private fun parseUiOverview(rawJson: String, generatedAtMs: Long): UiOverviewSnapshot {
        return try {
            val obj = JSONObject(rawJson)
            val core = obj.optJSONObject("core")?.optJSONObject("data")
            val connection = obj.optJSONObject("connection")?.optJSONObject("data")
            val displayScene = obj.optJSONObject("display_scene")?.optJSONObject("data")
            val approvals = obj.optJSONObject("approvals")?.optJSONObject("data")
            val attention = obj.optJSONObject("attention")?.optJSONObject("data")
            val notifications = obj.optJSONObject("notifications")?.optJSONObject("data")
            val task = obj.optJSONObject("current_task")?.optJSONObject("data")
            val tasks = obj.optJSONObject("tasks")?.optJSONObject("data")
            val memory = obj.optJSONObject("memory")?.optJSONObject("data")
            val mindSummary = obj.optJSONObject("mind_summary")?.optJSONObject("data")
            val freshness = obj.optJSONObject("freshness")
            val servers = obj.optJSONObject("servers")?.optJSONObject("data")?.optJSONArray("items")
            UiOverviewSnapshot(
                rawJson = rawJson,
                schemaVersion = obj.optString("schema_version", ""),
                generatedAtMs = generatedAtMs,
                coreMode = core?.optString("mode", "IDLE") ?: "IDLE",
                coreHealth = core?.optString("health", "UNKNOWN") ?: "UNKNOWN",
                missionPhase = displayScene?.optString("phase", "")?.takeIf { it.isNotBlank() }
                    ?: task?.optString("phase", "")?.takeIf { it.isNotBlank() }
                    ?: "Idle",
                connectionQuality = connection?.optString("quality", "Not reported") ?: "Not reported",
                freshnessStale = freshness?.optBoolean("stale", false) ?: false,
                pendingApprovals = approvals?.optInt("pending_count", 0) ?: 0,
                attentionCount = attention?.optInt("count", 0) ?: 0,
                unreadNotifications = notifications?.optInt("unread_count", 0) ?: 0,
                activeGoal = core?.optString("active_goal", "Not reported")?.ifBlank { "Not reported" } ?: "Not reported",
                activeTaskTitle = task?.optString("title", "No active task")?.ifBlank { "No active task" } ?: "No active task",
                taskPhase = task?.optString("phase", "Not reported")?.ifBlank { "Not reported" } ?: "Not reported",
                currentAction = task?.optString("current_action", "") ?: "",
                nextAction = task?.optString("next_action", "") ?: "",
                blockedReason = task?.optString("blocked_reason", "") ?: "",
                activeTaskCount = tasks?.optJSONArray("active")?.length() ?: 0,
                waitingTaskCount = tasks?.optJSONArray("waiting")?.length() ?: 0,
                scheduledTaskCount = tasks?.optJSONArray("scheduled")?.length() ?: 0,
                memorySummary = summarizeMobileMemory(memory, mindSummary),
                lastConsolidation = lastConsolidation(memory, mindSummary),
                servers = parseUiServers(servers),
            )
        } catch (exc: Exception) {
            UiOverviewSnapshot(rawJson = rawJson, generatedAtMs = generatedAtMs)
        }
    }

    private fun parseUiServers(items: org.json.JSONArray?): List<UiServerSummary> {
        if (items == null) return emptyList()
        val servers = mutableListOf<UiServerSummary>()
        for (index in 0 until items.length()) {
            val item = items.optJSONObject(index) ?: continue
            val serverId = item.optString("server_id", "")
            if (serverId.isBlank()) continue
            servers.add(
                UiServerSummary(
                    serverId = serverId,
                    label = item.optString("label", serverId.removeSuffix("-server")),
                    status = item.optString("status", "UNKNOWN"),
                    mode = item.optString("mode", ""),
                    detail = item.optString("status_detail", item.optString("degraded_reason", item.optString("recovery_hint", ""))),
                    heartbeatAgeSeconds = item.optLong("heartbeat_age_seconds", -1L),
                )
            )
        }
        return servers
    }

    private fun summarizeMobileMemory(memory: JSONObject?, mindSummary: JSONObject?): String {
        val memoryData = memory?.optJSONObject("summary") ?: memory ?: mindSummary?.optJSONObject("memory")
        if (memoryData == null) return "Not reported"
        val episodic = memoryData.optInt("episodic", -1)
        val semantic = memoryData.optInt("semantic", -1)
        val procedural = memoryData.optInt("procedural", -1)
        val known = listOf(episodic, semantic, procedural).filter { it >= 0 }
        return if (known.isNotEmpty()) {
            "E ${episodic.coerceAtLeast(0)} / S ${semantic.coerceAtLeast(0)} / P ${procedural.coerceAtLeast(0)}"
        } else {
            memoryData.optString("summary", "Not reported").ifBlank { "Not reported" }
        }
    }

    private fun lastConsolidation(memory: JSONObject?, mindSummary: JSONObject?): String {
        val memoryData = memory?.optJSONObject("summary") ?: memory ?: mindSummary?.optJSONObject("memory")
        return memoryData?.optString("last_consolidation", "")
            ?.ifBlank { memoryData.optString("last_consolidated_at", "") }
            ?.ifBlank { memoryData.optString("last_sleep_at", "") }
            ?.ifBlank { "Not reported" }
            ?: "Not reported"
    }

    private fun startMobileDashboardRefresh() {
        dashboardRefreshJob?.cancel()
        dashboardRefreshJob = scope.launch {
            while (isActive) {
                delay(15_000L)
                if (connected) {
                    refreshMobileDashboardState()
                    refreshUiOverview()
                }
            }
        }
    }

    private fun mergeChatMessages(incoming: List<MobileChatMessage>) {
        if (incoming.isEmpty()) return
        val merged = (_chatMessages.value + incoming)
            .distinctBy { message ->
                message.messageId.ifBlank { "${message.timestampMs}:${message.role}:${message.text}" }
            }
            .sortedWith(
                compareBy<MobileChatMessage> { it.timestampMs }
                    .thenBy { roleOrder(it.role) }
                    .thenBy { it.messageId }
            )
            .takeLast(120)
        _chatMessages.value = merged
    }

    private fun roleOrder(role: String): Int {
        return when (role.lowercase()) {
            "user" -> 0
            "assistant" -> 1
            else -> 2
        }
    }

    private fun updateState(
        connected: Boolean = _state.value.connected,
        connecting: Boolean = _state.value.connecting,
        lastHeartbeatMs: Long = _state.value.lastHeartbeatMs,
        lastError: String = _state.value.lastError,
        nextRetryMs: Long = _state.value.nextRetryMs,
        coreVersion: String = _state.value.coreVersion,
        chatRpcAvailable: Boolean = _state.value.chatRpcAvailable,
    ) {
        _state.value = AegisConnectionState(
            connected = connected,
            connecting = connecting,
            lastHeartbeatMs = lastHeartbeatMs,
            lastError = lastError,
            nextRetryMs = nextRetryMs,
            host = config.host,
            port = config.port,
            coreVersion = coreVersion,
            chatRpcAvailable = chatRpcAvailable,
        )
    }
}
