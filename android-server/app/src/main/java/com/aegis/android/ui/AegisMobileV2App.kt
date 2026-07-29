package com.aegis.android.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ChatBubbleOutline
import androidx.compose.material.icons.outlined.Checklist
import androidx.compose.material.icons.outlined.Devices
import androidx.compose.material.icons.outlined.FactCheck
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.MoreHoriz
import androidx.compose.material.icons.outlined.Security
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationRail
import androidx.compose.material3.NavigationRailItem
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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
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
import com.aegis.android.ui.feature.settings.ConnectionSaveRequest
import com.aegis.android.ui.feature.settings.SettingsScreen
import com.aegis.android.ui.feature.tasks.TasksScreen
import com.aegis.android.ui.model.MobilePermissionSnapshot
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

data class MobileUiActions(
    val permissionAction: (String) -> Unit,
    val saveConnection: (ConnectionSaveRequest) -> Unit,
    val connect: () -> Unit,
)

enum class MobileNavigationMode { BOTTOM, RAIL }

fun mobileNavigationMode(widthDp: Int, fontScale: Float = 1f): MobileNavigationMode =
    if (widthDp >= 600 && fontScale < 1.5f) MobileNavigationMode.RAIL else MobileNavigationMode.BOTTOM

private data class Tab(val route: String, val label: String, val icon: ImageVector)

private val tabs = listOf(
    Tab("home", "Home", Icons.Outlined.Home),
    Tab("chat", "Chat", Icons.Outlined.ChatBubbleOutline),
    Tab("approvals", "Approvals", Icons.Outlined.FactCheck),
    Tab("tasks", "Tasks", Icons.Outlined.Checklist),
    Tab("devices", "Devices", Icons.Outlined.Devices),
    Tab("permissions", "Permissions", Icons.Outlined.Security),
    Tab("settings", "Settings", Icons.Outlined.Settings),
)

private val compactTabs = tabs.take(4) + Tab("more", "More", Icons.Outlined.MoreHoriz)

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

    fun navigate(route: String) {
        navController.navigate(route) {
            launchSingleTop = true
            popUpTo("home")
        }
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

    val content: @Composable (Modifier) -> Unit = { modifier ->
        Box(modifier = modifier.background(AegisBackground)) {
            NavHost(navController = navController, startDestination = "home", modifier = Modifier.fillMaxSize()) {
                composable("home") {
                    HomeScreen(state = state, overview = overview, permissions = permissions, servers = servers)
                }
                composable("chat") { ChatScreen(client = client, messages = messages) }
                composable("approvals") {
                    ApprovalsScreen(client = client, approvals = approvals, onRefresh = ::refreshApprovals)
                }
                composable("tasks") { TasksScreen(overview = overview) }
                composable("devices") { DevicesScreen(servers = servers, overview = overview) }
                composable("permissions") {
                    PermissionsScreen(snapshot = permissions, onAction = actions.permissionAction)
                }
                composable("settings") {
                    SettingsScreen(config = config, onSave = actions.saveConnection, onConnect = actions.connect)
                }
                composable("more") { MoreScreen(onNavigate = ::navigate) }
            }
        }
    }

    AegisTheme {
        BoxWithConstraints(modifier = Modifier.fillMaxSize()) {
            val mode = mobileNavigationMode(maxWidth.value.toInt(), LocalDensity.current.fontScale)
            val backStack by navController.currentBackStackEntryAsState()
            val currentRoute = backStack?.destination?.route ?: "home"

            if (mode == MobileNavigationMode.RAIL) {
                Row(modifier = Modifier.fillMaxSize().background(AegisBackground)) {
                    NavigationRail(containerColor = AegisSurface, modifier = Modifier.width(104.dp)) {
                        tabs.forEach { tab ->
                            NavigationRailItem(
                                selected = currentRoute == tab.route,
                                onClick = { navigate(tab.route) },
                                label = { Text(tab.label, maxLines = 1) },
                                icon = { NavIcon(tab, currentRoute == tab.route) },
                            )
                        }
                    }
                    content(Modifier.fillMaxSize())
                }
            } else {
                Scaffold(
                    containerColor = AegisBackground,
                    bottomBar = {
                        NavigationBar(containerColor = AegisSurface) {
                            compactTabs.forEach { tab ->
                                val selected = currentRoute == tab.route ||
                                    (tab.route == "more" && currentRoute in setOf("devices", "permissions", "settings"))
                                NavigationBarItem(
                                    selected = selected,
                                    onClick = { navigate(tab.route) },
                                    label = { Text(tab.label, maxLines = 1) },
                                    icon = { NavIcon(tab, selected) },
                                )
                            }
                        }
                    },
                ) { padding -> content(Modifier.fillMaxSize().padding(padding)) }
            }
        }
    }
}

@Composable
private fun NavIcon(tab: Tab, selected: Boolean) {
    Icon(
        imageVector = tab.icon,
        contentDescription = tab.label,
        tint = if (selected) AegisText else AegisTextSecondary,
    )
}

@Composable
private fun MoreScreen(onNavigate: (String) -> Unit) {
    Box(modifier = Modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.TopStart) {
        Column {
            Text("More", color = AegisText, style = MaterialTheme.typography.headlineSmall)
            tabs.drop(4).forEach { tab ->
                FilledTonalButton(
                    onClick = { onNavigate(tab.route) },
                    modifier = Modifier.padding(top = 12.dp),
                ) {
                    Icon(tab.icon, contentDescription = null)
                    Text(tab.label, modifier = Modifier.padding(start = 10.dp))
                }
            }
        }
    }
}
