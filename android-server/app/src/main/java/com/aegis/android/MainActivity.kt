package com.aegis.android

import android.Manifest
import android.app.Activity
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.text.TextUtils
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.aegis.android.grpc.AegisConnectionState
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.grpc.ApprovalItem
import com.aegis.android.grpc.MobileChatMessage
import com.aegis.android.grpc.MobileServerStatus
import com.aegis.android.notification.AegisNotificationListener
import com.aegis.android.overlay.OverlayController
import com.aegis.android.provider.DeviceProvider
import com.aegis.android.provider.LocationProvider
import com.aegis.android.provider.ScreenshotProvider
import com.aegis.android.provider.UITreeProvider
import com.aegis.android.service.AegisAccessibilityService
import com.aegis.android.service.ScreenshotService
import com.aegis.android.ui.AegisMobileV2App
import com.aegis.android.ui.MobileUiActions
import com.aegis.android.ui.model.MobilePermissionSnapshot
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    companion object {
        private const val TAG = "AegisMainActivity"
        private const val REQUEST_MEDIA_PROJECTION = 1001
        private const val REQUEST_LOCATION = 1002
        private const val REQUEST_NOTIFICATIONS = 1003
    }

    private lateinit var grpcClient: AegisGrpcClient
    private lateinit var deviceProvider: DeviceProvider
    private lateinit var screenshotProvider: ScreenshotProvider
    private lateinit var uiTreeProvider: UITreeProvider
    private lateinit var locationProvider: LocationProvider
    private lateinit var overlayController: OverlayController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        deviceProvider = DeviceProvider(this)
        screenshotProvider = ScreenshotProvider(this)
        uiTreeProvider = UITreeProvider(this)
        locationProvider = LocationProvider(this)
        overlayController = OverlayController(this)
        grpcClient = AegisGrpcClient.getInstance(this)

        bindAccessibilityProvider()
        applyIntentConfig(intent)
        startForegroundService(Intent(this, AegisForegroundService::class.java))

        setContent {
            val scope = rememberCoroutineScope()
            var config by remember { mutableStateOf(AegisConfig.load(this@MainActivity)) }
            var client by remember { mutableStateOf(grpcClient) }
            AegisMobileV2App(
                client = client,
                config = config,
                permissionsProvider = { buildMobilePermissionSnapshot() },
                actions = MobileUiActions(
                    permissionAction = { action ->
                        when (action) {
                            "notification-runtime" -> requestRuntimeNotificationPermission()
                            "notification-access" -> openNotificationAccessSettings()
                            "accessibility" -> openAccessibilitySettings()
                            "screenshot" -> requestScreenshotPermission()
                            "overlay" -> openOverlaySettings()
                            "location" -> requestLocationPermission()
                        }
                    },
                    saveConnection = { host, port, token ->
                        config = AegisConfig.save(this@MainActivity, host, port, token)
                        client = AegisGrpcClient.getInstance(this@MainActivity)
                        grpcClient = client
                    },
                    connect = {
                        scope.launch(Dispatchers.IO) { client.connect() }
                    },
                ),
            )
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        applyIntentConfig(intent)
    }

    override fun onResume() {
        super.onResume()
        bindAccessibilityProvider()
        grpcClient.pushPermissionChanged()
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_MEDIA_PROJECTION && resultCode == Activity.RESULT_OK && data != null) {
            screenshotProvider.setMediaProjectionResult(resultCode, data)
            Log.i(TAG, "Screenshot permission granted")
            grpcClient.pushPermissionChanged()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_LOCATION || requestCode == REQUEST_NOTIFICATIONS) {
            grpcClient.pushPermissionChanged()
        }
    }

    @Composable
    private fun AegisAndroidApp() {
        var selectedTab by remember { mutableStateOf("Home") }
        var client by remember { mutableStateOf(grpcClient) }
        var snapshot by remember { mutableStateOf(buildStatusSnapshot()) }

        LaunchedEffect(client) {
            while (true) {
                bindAccessibilityProvider()
                snapshot = buildStatusSnapshot()
                delay(2_000L)
            }
        }

        MaterialTheme(colorScheme = AegisScheme) {
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = AegisBlack,
            ) {
                Scaffold(
                    containerColor = Color.Transparent,
                    bottomBar = {
                        NavigationBar(
                            containerColor = AegisPanel,
                            tonalElevation = 0.dp,
                        ) {
                            listOf("State", "Home", "Action").forEach { tab ->
                                NavigationBarItem(
                                    selected = selectedTab == tab,
                                    onClick = { selectedTab = tab },
                                    label = { Text(tab, fontWeight = if (selectedTab == tab) FontWeight.Bold else FontWeight.Normal) },
                                    icon = {
                                        Box(
                                            modifier = Modifier
                                                .size(if (selectedTab == tab) 8.dp else 6.dp)
                                                .background(
                                                    if (selectedTab == tab) AegisPurple else AegisMuted,
                                                    RoundedCornerShape(50),
                                                ),
                                        )
                                    },
                                    colors = NavigationBarItemDefaults.colors(
                                        selectedIconColor = AegisPurple,
                                        selectedTextColor = AegisText,
                                        unselectedIconColor = AegisMuted,
                                        unselectedTextColor = AegisMuted,
                                        indicatorColor = AegisPurpleDeep.copy(alpha = 0.34f),
                                    ),
                                )
                            }
                        }
                    },
                ) { padding ->
                    Box(
                        modifier = Modifier
                            .padding(padding)
                            .fillMaxSize()
                            .background(
                                Brush.verticalGradient(
                                    listOf(AegisBlack, Color(0xFF0A0714), AegisBlack),
                                ),
                            )
                            .padding(16.dp),
                    ) {
                        when (selectedTab) {
                            "State" -> StateTab(
                                snapshot = snapshot,
                                client = client,
                                onClientChanged = {
                                    client = it
                                    grpcClient = it
                                },
                            )
                            "Action" -> ActionTab(client)
                            else -> HomeTab(snapshot, client)
                        }
                    }
                }
            }
        }
    }

    @Composable
    private fun HomeTab(snapshot: StatusSnapshot, client: AegisGrpcClient) {
        val state by client.state.collectAsState()
        val serverStatuses by client.serverStatuses.collectAsState()
        val sharedMessages by client.chatMessages.collectAsState()
        val scope = rememberCoroutineScope()
        val transientMessages = remember { mutableStateListOf<ChatMessage>() }
        var input by remember { mutableStateOf("") }
        var conversationId by remember { mutableStateOf("") }
        var sending by remember { mutableStateOf(false) }
        val messages = sharedMessages.map { it.toChatMessage() } + transientMessages

        Column(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            HomeStatusStrip(state, serverStatuses)
            WarningPanel(snapshot, state)
            Text("Chat", style = MaterialTheme.typography.titleMedium, color = AegisText, fontWeight = FontWeight.Bold)
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(messages) { message ->
                    ChatBubble(message)
                }
            }
            CyberPanel(accent = AegisPurple) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                    OutlinedTextField(
                        modifier = Modifier.weight(1f),
                        value = input,
                        onValueChange = { input = it },
                        label = { Text("Message") },
                        minLines = 1,
                        maxLines = 3,
                        colors = fieldColors(),
                    )
                    Button(
                        enabled = input.isNotBlank() && !sending,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = AegisPurple,
                            contentColor = Color.White,
                            disabledContainerColor = AegisPanelAlt,
                            disabledContentColor = AegisMuted,
                        ),
                        onClick = {
                            val text = input.trim()
                            input = ""
                            sending = true
                            scope.launch(Dispatchers.Main) {
                                val reply = client.sendChat(text, conversationId)
                                conversationId = reply.conversationId.ifBlank { conversationId }
                                if (!reply.ok) {
                                    transientMessages.add(ChatMessage("AEGIS", "Error: ${reply.error}"))
                                } else if (reply.approvalNeeded) {
                                    transientMessages.add(ChatMessage("AEGIS", "Approval required: ${reply.approvalId}"))
                                }
                                sending = false
                            }
                        },
                    ) {
                        Text(if (sending) "..." else "Send")
                    }
                }
            }
        }
    }

    @Composable
    private fun HomeStatusStrip(state: AegisConnectionState, serverStatuses: List<MobileServerStatus>) {
        CyberPanel(accent = if (state.connected) AegisGreen else AegisRed) {
            CoreStatusHeader(
                status = if (state.connected) "ONLINE" else if (state.connecting) "DEGRADED" else "OFFLINE",
            )
            Spacer(Modifier.height(12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                listOf(
                    "ai-server" to "AI",
                    "pc-server" to "PC",
                    "browser-server" to "Browser",
                ).forEach { (serverId, label) ->
                    val status = serverStatuses.firstOrNull { it.serverId == serverId }?.status ?: "UNKNOWN"
                    ServerDot(label, status)
                }
            }
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                listOf(
                    "android-server" to "Android",
                    "room-server" to "Room",
                ).forEach { (serverId, label) ->
                    val status = serverStatuses.firstOrNull { it.serverId == serverId }?.status ?: "UNKNOWN"
                    ServerDot(label, status)
                }
            }
        }
    }

    @Composable
    private fun WarningPanel(snapshot: StatusSnapshot, state: AegisConnectionState) {
        val warnings = buildList {
            if (!state.connected) add("AEGIS Core is not connected")
            if (!state.chatRpcAvailable) add("Chat RPC support is unknown")
            if (!snapshot.notificationRuntime) add("Notification permission is missing")
            if (!snapshot.notificationAccess) add("Notification access is missing")
            if (!snapshot.accessibility) add("Accessibility permission is missing")
            if (!snapshot.screenshot) add("Screenshot permission is missing")
            if (!snapshot.overlay) add("Overlay permission is missing")
            if (!snapshot.location) add("Location permission is missing")
            if (state.lastError.isNotBlank()) add(state.lastError)
        }.distinct()
        if (warnings.isEmpty()) return
        CyberPanel(accent = AegisAmber) {
            warnings.take(4).forEach { warning ->
                Text(warning, color = AegisAmber, style = MaterialTheme.typography.bodySmall)
            }
        }
    }

    @Composable
    private fun StateTab(
        snapshot: StatusSnapshot,
        client: AegisGrpcClient,
        onClientChanged: (AegisGrpcClient) -> Unit,
    ) {
        val state by client.state.collectAsState()
        val scope = rememberCoroutineScope()
        var config by remember { mutableStateOf(AegisConfig.load(this)) }
        var host by remember { mutableStateOf(config.host) }
        var portText by remember { mutableStateOf(config.port.toString()) }
        var token by remember { mutableStateOf(config.pairingToken) }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Header("STATE MATRIX", "Core, permissions, device telemetry")
            StatusCard(snapshot, state)
            CyberPanel(accent = AegisCyan) {
                Text("Core link", style = MaterialTheme.typography.titleMedium, color = AegisText, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(10.dp))
                OutlinedTextField(host, { host = it }, label = { Text("AEGIS Core host") }, modifier = Modifier.fillMaxWidth(), colors = fieldColors())
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(portText, { portText = it }, label = { Text("AEGIS Core gRPC port") }, modifier = Modifier.fillMaxWidth(), colors = fieldColors())
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    token,
                    { token = it },
                    label = { Text("Pairing token") },
                    visualTransformation = PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth(),
                    colors = fieldColors(),
                )
                Spacer(Modifier.height(10.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        colors = purpleButtonColors(),
                        onClick = {
                            config = AegisConfig.save(this@MainActivity, host, portText.toIntOrNull() ?: 50051, token)
                            val nextClient = AegisGrpcClient.getInstance(this@MainActivity)
                            grpcClient = nextClient
                            onClientChanged(nextClient)
                            startForegroundService(Intent(this@MainActivity, AegisForegroundService::class.java))
                            scope.launch { nextClient.connect() }
                        },
                    ) {
                        Text(if (state.connected) "Reconnect" else "Connect")
                    }
                    TextButton(onClick = { startForegroundService(Intent(this@MainActivity, AegisForegroundService::class.java)) }) {
                        Text("Start service", color = AegisCyan)
                    }
                }
            }
            CyberPanel(accent = AegisPurple) {
                Text("Permissions", style = MaterialTheme.typography.titleMedium, color = AegisText, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                PermissionButton("Notification runtime", snapshot.notificationRuntime) { requestRuntimeNotificationPermission() }
                PermissionButton("Notification access", snapshot.notificationAccess) { openNotificationAccessSettings() }
                PermissionButton("Accessibility", snapshot.accessibility) { openAccessibilitySettings() }
                PermissionButton("Screenshot", snapshot.screenshot) { requestScreenshotPermission() }
                PermissionButton("Overlay", snapshot.overlay) { openOverlaySettings() }
                PermissionButton("Location", snapshot.location) { requestLocationPermission() }
            }
            CyberPanel(accent = AegisGreen) {
                Text("Device", style = MaterialTheme.typography.titleMedium, color = AegisText, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                InfoLine("Device", snapshot.deviceLine)
                InfoLine("Battery", snapshot.batteryLine)
                InfoLine("Screen", snapshot.screenLine)
                InfoLine("Last heartbeat", state.lastHeartbeatMs.takeIf { it > 0 }?.toString() ?: "-")
                InfoLine("Next retry", state.nextRetryMs.takeIf { it > 0 }?.toString() ?: "-")
            }
        }
    }

    @Composable
    private fun ActionTab(client: AegisGrpcClient) {
        val scope = rememberCoroutineScope()
        var approvals by remember { mutableStateOf<List<ApprovalItem>>(emptyList()) }
        var actionResult by remember { mutableStateOf("") }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Header("ACTION BAY", "Approvals and direct controls")
            CyberPanel(accent = AegisRed) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                    Button(
                        colors = ButtonDefaults.buttonColors(containerColor = AegisPurple, contentColor = Color.White),
                        onClick = { scope.launch { approvals = client.listPendingApprovals() } },
                    ) {
                        Text("Refresh approvals")
                    }
                    Button(
                        colors = ButtonDefaults.buttonColors(containerColor = AegisRed, contentColor = Color.White),
                        onClick = {
                            scope.launch {
                                val reply = client.invokeTool("android-server.safety.emergency_stop", "{}")
                                actionResult = if (reply.ok) reply.output else "Error: ${reply.error}"
                            }
                        },
                    ) {
                        Text("Emergency stop")
                    }
                }
            }
            CyberPanel(accent = AegisCyan) {
                Text("Pending approvals", style = MaterialTheme.typography.titleMedium, color = AegisText, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                if (approvals.isEmpty()) {
                    Text("No pending approvals.", color = AegisMuted)
                } else {
                    approvals.forEach { approval ->
                        ApprovalCard(approval, client) {
                            scope.launch { approvals = client.listPendingApprovals() }
                        }
                    }
                }
            }
            if (actionResult.isNotBlank()) {
                CyberPanel(accent = AegisAmber) {
                    Text(actionResult, color = AegisText)
                }
            }
        }
    }

    @Composable
    private fun StatusCard(snapshot: StatusSnapshot, state: AegisConnectionState) {
        CyberPanel(accent = if (state.connected) AegisGreen else AegisRed) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                StatusPill(
                    if (state.connected) "Connected" else if (state.connecting) "Connecting" else "Disconnected",
                    if (state.connected) AegisGreen else if (state.connecting) AegisAmber else AegisRed,
                )
                StatusPill(
                    if (state.chatRpcAvailable) "Chat RPC ready" else "Chat RPC unknown",
                    if (state.chatRpcAvailable) AegisCyan else AegisAmber,
                )
            }
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                StatusPill(if (snapshot.screenshot) "Screenshot OK" else "Screenshot needed", if (snapshot.screenshot) AegisGreen else AegisAmber)
                StatusPill(if (snapshot.accessibility) "Accessibility OK" else "Accessibility needed", if (snapshot.accessibility) AegisGreen else AegisAmber)
            }
            Spacer(Modifier.height(10.dp))
            InfoLine("Core", "${state.host}:${state.port}")
            InfoLine("Version", state.coreVersion.ifBlank { "-" })
            InfoLine("Device", snapshot.deviceLine)
            InfoLine("Screen", snapshot.screenLine)
            if (state.lastError.isNotBlank()) {
                Spacer(Modifier.height(8.dp))
                Text("Last error: ${state.lastError}", color = AegisRed, style = MaterialTheme.typography.bodySmall)
            }
        }
    }

    @Composable
    private fun PermissionButton(label: String, granted: Boolean, onClick: () -> Unit) {
        Column {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(label, color = AegisText)
                    Text(if (granted) "Granted" else "Missing", color = if (granted) AegisGreen else AegisAmber, style = MaterialTheme.typography.bodySmall)
                }
                Button(enabled = !granted, onClick = onClick, colors = purpleButtonColors()) {
                    Text("Open")
                }
            }
            HorizontalDivider(color = AegisPurple.copy(alpha = 0.18f))
        }
    }

    @Composable
    private fun ApprovalCard(approval: ApprovalItem, client: AegisGrpcClient, onDone: () -> Unit) {
        val scope = rememberCoroutineScope()
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 5.dp)
                .border(1.dp, AegisPurple.copy(alpha = 0.35f), RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = AegisPanelAlt),
            shape = RoundedCornerShape(8.dp),
        ) {
            Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(approval.capabilityId, style = MaterialTheme.typography.titleSmall, color = AegisText, fontWeight = FontWeight.Bold)
                Text(approval.summary.ifBlank { approval.approvalId }, color = AegisMuted)
                if (approval.risk.isNotBlank()) Text(approval.risk, color = AegisAmber, style = MaterialTheme.typography.bodySmall)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        colors = ButtonDefaults.buttonColors(containerColor = AegisGreen, contentColor = AegisBlack),
                        onClick = {
                            scope.launch {
                                client.resolveApproval(approval.approvalId, true)
                                onDone()
                            }
                        },
                    ) { Text("Approve") }
                    TextButton(
                        onClick = {
                            scope.launch {
                                client.resolveApproval(approval.approvalId, false)
                                onDone()
                            }
                        },
                    ) { Text("Reject", color = AegisRed) }
                }
            }
        }
    }

    @Composable
    private fun ChatBubble(message: ChatMessage) {
        val isUser = message.role == "You"
        val accent = if (isUser) AegisCyan else AegisPurple
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, accent.copy(alpha = 0.35f), RoundedCornerShape(8.dp)),
            colors = CardDefaults.cardColors(containerColor = if (isUser) Color(0xFF0C1A24) else AegisPanelAlt),
            shape = RoundedCornerShape(8.dp),
        ) {
            Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(message.role, style = MaterialTheme.typography.labelMedium, color = accent, fontWeight = FontWeight.Bold)
                Text(message.text, color = AegisText)
            }
        }
    }

    @Composable
    private fun Header(title: String, subtitle: String) {
        Column {
            Text(title, style = MaterialTheme.typography.headlineSmall, color = AegisText, fontWeight = FontWeight.ExtraBold)
            Text(subtitle, style = MaterialTheme.typography.bodySmall, color = AegisCyan)
        }
    }

    @Composable
    private fun CyberPanel(accent: Color, content: @Composable ColumnScope.() -> Unit) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(
                    BorderStroke(1.dp, accent.copy(alpha = 0.45f)),
                    RoundedCornerShape(8.dp),
                ),
            colors = CardDefaults.cardColors(containerColor = AegisPanel),
            shape = RoundedCornerShape(8.dp),
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        Brush.linearGradient(
                            listOf(accent.copy(alpha = 0.08f), AegisPanel, AegisPanel),
                        ),
                    )
                    .padding(12.dp),
                content = content,
            )
        }
    }

    @Composable
    private fun StatusPill(text: String, color: Color) {
        Card(
            colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.12f)),
            border = BorderStroke(1.dp, color.copy(alpha = 0.6f)),
            shape = RoundedCornerShape(50),
        ) {
            Text(
                text,
                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                color = color,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold,
            )
        }
    }

    @Composable
    private fun ServerDot(label: String, status: String) {
        val color = statusColor(status)
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(label, color = AegisText, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
            Box(
                modifier = Modifier
                    .size(10.dp)
                    .background(color, RoundedCornerShape(50)),
            )
        }
    }

    @Composable
    private fun CoreStatusHeader(status: String) {
        val color = statusColor(status)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                "AEGIS Core",
                style = MaterialTheme.typography.headlineSmall,
                color = AegisText,
                fontWeight = FontWeight.ExtraBold,
            )
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(status, color = color, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                Box(
                    modifier = Modifier
                        .size(16.dp)
                        .background(color, RoundedCornerShape(50)),
                )
            }
        }
    }

    @Composable
    private fun InfoLine(label: String, value: String) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(label, color = AegisMuted, style = MaterialTheme.typography.bodySmall)
            Text(value, color = AegisText, style = MaterialTheme.typography.bodySmall)
        }
    }

    @Composable
    private fun fieldColors() = OutlinedTextFieldDefaults.colors(
        focusedTextColor = AegisText,
        unfocusedTextColor = AegisText,
        focusedBorderColor = AegisPurple,
        unfocusedBorderColor = AegisMuted.copy(alpha = 0.45f),
        focusedLabelColor = AegisCyan,
        unfocusedLabelColor = AegisMuted,
        cursorColor = AegisPurple,
        focusedContainerColor = AegisPanelAlt,
        unfocusedContainerColor = AegisPanelAlt,
    )

    @Composable
    private fun purpleButtonColors() = ButtonDefaults.buttonColors(
        containerColor = AegisPurpleDeep,
        contentColor = Color.White,
        disabledContainerColor = AegisPanelAlt,
        disabledContentColor = AegisMuted,
    )

    private fun statusColor(status: String): Color {
        return when (status.uppercase()) {
            "ONLINE" -> AegisGreen
            "DEGRADED", "UNKNOWN" -> AegisAmber
            "OFFLINE" -> AegisRed
            "DISABLED", "UNCONFIGURED" -> AegisMuted
            else -> AegisAmber
        }
    }

    private fun MobileChatMessage.toChatMessage(): ChatMessage {
        val roleLabel = if (role == "user") "You" else "AEGIS"
        return ChatMessage(roleLabel, text)
    }

    private fun buildStatusSnapshot(): StatusSnapshot {
        val device = deviceProvider.getDeviceInfo()
        return StatusSnapshot(
            notificationRuntime = hasRuntimeNotificationPermission(),
            notificationAccess = AegisNotificationListener.isEnabled(this),
            accessibility = isAccessibilityServiceEnabled(),
            screenshot = screenshotProvider.isAvailable(),
            overlay = overlayController.canDrawOverlays(),
            location = locationProvider.hasPermission(),
            deviceLine = "${device.manufacturer} ${device.model} / Android ${device.androidVersion}",
            batteryLine = "${device.batteryLevel}%${if (device.batteryCharging) " charging" else ""}",
            screenLine = "${if (device.screenOn) "On" else "Off"} / ${if (device.locked) "Locked" else "Unlocked"}",
        )
    }

    private fun buildMobilePermissionSnapshot(): MobilePermissionSnapshot {
        val snapshot = buildStatusSnapshot()
        return MobilePermissionSnapshot(
            notificationRuntime = snapshot.notificationRuntime,
            notificationAccess = snapshot.notificationAccess,
            accessibility = snapshot.accessibility,
            screenshot = snapshot.screenshot,
            overlay = snapshot.overlay,
            location = snapshot.location,
        )
    }

    private fun bindAccessibilityProvider() {
        AegisAccessibilityService.instance?.let { uiTreeProvider.setAccessibilityService(it) }
    }

    private fun hasRuntimeNotificationPermission(): Boolean {
        return Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val enabledServices = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES)
        if (TextUtils.isEmpty(enabledServices)) return false
        val myComponent = ComponentName(this, AegisAccessibilityService::class.java).flattenToString()
        return enabledServices?.split(":")?.any { it == myComponent } == true
    }

    private fun openNotificationAccessSettings() {
        startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
    }

    private fun openAccessibilitySettings() {
        startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
    }

    private fun openOverlaySettings() {
        startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName")))
    }

    private fun requestRuntimeNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), REQUEST_NOTIFICATIONS)
        }
    }

    private fun requestLocationPermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION),
            REQUEST_LOCATION,
        )
    }

    private fun requestScreenshotPermission() {
        val serviceIntent = Intent(this, ScreenshotService::class.java)
        startForegroundService(serviceIntent)
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        startActivityForResult(projectionManager.createScreenCaptureIntent(), REQUEST_MEDIA_PROJECTION)
    }

    private fun applyIntentConfig(intent: Intent?) {
        intent ?: return
        val host = intent.getStringExtra("host")
        val token = intent.getStringExtra("pairing_token")
        val port = if (intent.hasExtra("port")) intent.getIntExtra("port", 50051) else null
        if (host != null || token != null || port != null) {
            val current = AegisConfig.load(this)
            AegisConfig.save(
                this,
                host ?: current.host,
                port ?: current.port,
                token ?: current.pairingToken,
            )
            grpcClient = AegisGrpcClient.getInstance(this)
        }
        if (intent.getBooleanExtra("auto_connect", false)) {
            startForegroundService(Intent(this, AegisForegroundService::class.java))
        }
    }
}

data class StatusSnapshot(
    val notificationRuntime: Boolean,
    val notificationAccess: Boolean,
    val accessibility: Boolean,
    val screenshot: Boolean,
    val overlay: Boolean,
    val location: Boolean,
    val deviceLine: String,
    val batteryLine: String,
    val screenLine: String,
)

data class ChatMessage(
    val role: String,
    val text: String,
)

private val AegisBlack = Color(0xFF05060A)
private val AegisPanel = Color(0xFF10121D)
private val AegisPanelAlt = Color(0xFF171A2A)
private val AegisPurple = Color(0xFFA276FF)
private val AegisPurpleDeep = Color(0xFF6C3CFF)
private val AegisCyan = Color(0xFF38E8FF)
private val AegisGreen = Color(0xFF6DFFB0)
private val AegisAmber = Color(0xFFFFC857)
private val AegisRed = Color(0xFFFF5872)
private val AegisMuted = Color(0xFF8D93A8)
private val AegisText = Color(0xFFF1EEFF)

private val AegisScheme = darkColorScheme(
    primary = AegisPurple,
    secondary = AegisCyan,
    tertiary = AegisGreen,
    background = AegisBlack,
    surface = AegisPanel,
    surfaceVariant = AegisPanelAlt,
    error = AegisRed,
    onPrimary = Color.White,
    onSecondary = AegisBlack,
    onBackground = AegisText,
    onSurface = AegisText,
)
