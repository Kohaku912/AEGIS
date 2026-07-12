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

@Composable
fun DevicesScreen(servers: List<MobileServerStatus>) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxSize().padding(16.dp)) {
        items(servers) { server ->
            AegisPanel(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(server.label.ifBlank { server.serverId }, color = AegisText)
                    Text("${server.status} / ${server.mode}", color = AegisTextSecondary)
                    Text(server.detail.ifBlank { "No detail" }, color = AegisTextSecondary)
                }
            }
        }
    }
}
