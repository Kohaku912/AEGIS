package com.aegis.android.ui.feature.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.aegis.android.grpc.AegisConnectionState
import com.aegis.android.grpc.MobileServerStatus
import com.aegis.android.ui.designsystem.AegisPanel
import com.aegis.android.ui.designsystem.AegisText
import com.aegis.android.ui.designsystem.AegisTextSecondary
import com.aegis.android.ui.designsystem.CoreGlyph
import com.aegis.android.ui.model.MobilePermissionSnapshot
import com.aegis.android.ui.model.UiServerSummary
import com.aegis.android.ui.model.UiOverviewSnapshot

@Composable
fun HomeScreen(
    state: AegisConnectionState,
    overview: UiOverviewSnapshot,
    permissions: MobilePermissionSnapshot,
    servers: List<MobileServerStatus>,
) {
    val overviewServers = if (overview.servers.isNotEmpty()) {
        overview.servers
    } else {
        servers.map { UiServerSummary(it.serverId, it.label.ifBlank { it.serverId }, it.status, it.mode, it.detail) }
    }
    Column(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(16.dp)) {
        AegisPanel(modifier = Modifier.fillMaxWidth()) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(16.dp),
            ) {
                CoreGlyph(mode = overview.coreMode, health = overview.coreHealth, pendingApprovals = overview.pendingApprovals)
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("AEGIS Mobile", color = AegisText, fontWeight = FontWeight.Bold)
                    Text("Core: ${overview.coreMode} / ${overview.coreHealth} / ${overview.missionPhase}", color = AegisTextSecondary)
                    Text(if (state.connected) "Connected to ${state.host}:${state.port}" else "Disconnected: ${state.lastError.ifBlank { "waiting" }}", color = AegisTextSecondary)
                    Text("Current: ${overview.activeTaskTitle}", color = AegisTextSecondary)
                    Text("Next: ${overview.nextAction.ifBlank { overview.currentAction.ifBlank { "Not reported" } }}", color = AegisTextSecondary)
                }
            }
        }
        AegisPanel(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(16.dp)) {
                Text("Attention", color = AegisText, fontWeight = FontWeight.Bold)
                Text("Approvals ${overview.pendingApprovals} / Attention ${overview.attentionCount} / Notifications ${overview.unreadNotifications}", color = AegisTextSecondary)
                Text("Connection ${overview.connectionQuality}${if (overview.freshnessStale) " / stale" else ""}", color = AegisTextSecondary)
                Text("Memory ${overview.memorySummary}", color = AegisTextSecondary)
            }
        }
        AegisPanel(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(16.dp)) {
                Text("Permissions", color = AegisText, fontWeight = FontWeight.Bold)
                Text("Accessibility ${ok(permissions.accessibility)} / Notifications ${ok(permissions.notificationAccess)} / Screenshot ${ok(permissions.screenshot)}", color = AegisTextSecondary)
            }
        }
        AegisPanel(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(16.dp)) {
                Text("Systems", color = AegisText, fontWeight = FontWeight.Bold)
                overviewServers.take(6).forEach { server ->
                    Text("${server.label.ifBlank { server.serverId }}: ${server.status} ${server.detail}", color = AegisTextSecondary)
                }
            }
        }
    }
}

private fun ok(value: Boolean): String = if (value) "OK" else "Missing"
