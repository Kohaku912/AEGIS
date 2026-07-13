package com.aegis.android.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.aegis.android.AegisConnectionConfig
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.grpc.ApprovalItem
import com.aegis.android.ui.designsystem.AegisBackground
import com.aegis.android.ui.designsystem.AegisSurface
import com.aegis.android.ui.designsystem.AegisText
import com.aegis.android.ui.designsystem.AegisTextSecondary
import com.aegis.android.ui.designsystem.AegisTheme
import com.aegis.android.ui.feature.approvals.ApprovalsScreen
import com.aegis.android.ui.feature.chat.ChatScreen
import com.aegis.android.ui.feature.devices.DevicesScreen
import com.aegis.android.ui.feature.home.HomeScreen
import com.aegis.android.ui.feature.permissions.PermissionsScreen
import com.aegis.android.ui.feature.settings.SettingsScreen
import com.aegis.android.ui.feature.tasks.TasksScreen
import com.aegis.android.ui.model.MobilePermissionSnapshot
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

data class MobileUiActions(
    val permissionAction: (String) -> Unit,
    val saveConnection: (String, Int, String) -> Unit,
    val connect: () -> Unit,
)

private data class Tab(val route: String, val label: String)

private val tabs = listOf(
    Tab("home", "Home"),
    Tab("chat", "Chat"),
    Tab("approvals", "Approvals"),
    Tab("tasks", "Tasks"),
    Tab("devices", "Devices"),
    Tab("permissions", "Permissions"),
    Tab("settings", "Settings"),
)

@Composable
fun AegisMobileV2App(
    client: AegisGrpcClient,
    config: AegisConnectionConfig,
    permissionsProvider: () -> MobilePermissionSnapshot,
    actions: MobileUiActions,
) {
    val navController = rememberNavController()
    val state by client.state.collectAsState()
    val servers by client.serverStatuses.collectAsState()
    val messages by client.chatMessages.collectAsState()
    val overview by client.uiOverview.collectAsState()
    val scope = rememberCoroutineScope()
    var permissions by remember { mutableStateOf(permissionsProvider()) }
    var approvals by remember { mutableStateOf<List<ApprovalItem>>(emptyList()) }

    fun refreshApprovals() {
        scope.launch { approvals = client.listPendingApprovals() }
    }

    LaunchedEffect(client) {
        while (true) {
            permissions = permissionsProvider()
            client.refreshMobileDashboardState()
            client.refreshUiOverview()
            approvals = client.listPendingApprovals()
            delay(5_000L)
        }
    }

    AegisTheme {
        Scaffold(
            containerColor = AegisBackground,
            bottomBar = {
                NavigationBar(containerColor = AegisSurface) {
                    val backStack by navController.currentBackStackEntryAsState()
                    val currentRoute = backStack?.destination?.route ?: "home"
                    tabs.forEach { tab ->
                        NavigationBarItem(
                            selected = currentRoute == tab.route,
                            onClick = {
                                navController.navigate(tab.route) {
                                    launchSingleTop = true
                                    popUpTo("home")
                                }
                            },
                            label = { Text(tab.label, color = if (currentRoute == tab.route) AegisText else AegisTextSecondary) },
                            icon = { Text(tab.label.take(1), color = if (currentRoute == tab.route) AegisText else AegisTextSecondary) },
                        )
                    }
                }
            },
        ) { padding ->
            Box(modifier = Modifier.fillMaxSize().background(AegisBackground)) {
                NavHost(navController = navController, startDestination = "home", modifier = Modifier.fillMaxSize()) {
                    composable("home") {
                        HomeScreen(state = state, overview = overview, permissions = permissions, servers = servers)
                    }
                    composable("chat") {
                        ChatScreen(client = client, messages = messages)
                    }
                    composable("approvals") {
                        ApprovalsScreen(client = client, approvals = approvals, onRefresh = ::refreshApprovals)
                    }
                    composable("tasks") {
                        TasksScreen(overview = overview)
                    }
                    composable("devices") {
                        DevicesScreen(servers = servers, overview = overview)
                    }
                    composable("permissions") {
                        PermissionsScreen(snapshot = permissions, onAction = actions.permissionAction)
                    }
                    composable("settings") {
                        SettingsScreen(config = config, onSave = actions.saveConnection, onConnect = actions.connect)
                    }
                }
            }
        }
    }
}
