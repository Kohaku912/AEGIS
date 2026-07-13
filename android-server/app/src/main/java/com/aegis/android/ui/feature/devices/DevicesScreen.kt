package com.aegis.android.ui.feature.devices

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.aegis.android.grpc.MobileServerStatus
import com.aegis.android.ui.designsystem.AegisPanel
import com.aegis.android.ui.designsystem.AegisText
import com.aegis.android.ui.designsystem.AegisTextSecondary
import com.aegis.android.ui.model.UiOverviewSnapshot
import com.aegis.android.ui.model.UiServerSummary

@Composable
fun DevicesScreen(servers: List<MobileServerStatus>, overview: UiOverviewSnapshot) {
    val items = if (overview.servers.isNotEmpty()) {
        overview.servers
    } else {
        servers.map { UiServerSummary(it.serverId, it.label.ifBlank { it.serverId }, it.status, it.mode, it.detail) }
    }
    LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxSize().padding(16.dp)) {
        items(items) { server ->
            AegisPanel(modifier = Modifier.fillMaxWidth()) {
                Column(verticalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(16.dp)) {
                    Text(server.label.ifBlank { server.serverId }, color = AegisText)
                    Text("${server.status} / ${server.mode}", color = AegisTextSecondary)
                    Text(server.detail.ifBlank { "No detail" }, color = AegisTextSecondary)
                    if (server.heartbeatAgeSeconds >= 0) {
                        Text("Heartbeat ${server.heartbeatAgeSeconds}s ago", color = AegisTextSecondary)
                    }
                }
            }
        }
    }
}
