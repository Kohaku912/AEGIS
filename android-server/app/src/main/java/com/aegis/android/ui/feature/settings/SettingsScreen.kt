package com.aegis.android.ui.feature.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.aegis.android.AegisConnectionConfig
import com.aegis.android.ui.designsystem.AegisPanel
import com.aegis.android.ui.designsystem.AegisText
import com.aegis.android.ui.designsystem.AegisTextSecondary

data class ConnectionSaveRequest(
    val host: String,
    val port: Int,
    val pairingToken: String,
    val fallbackHost: String,
    val fallbackPort: Int,
    val useTlsFallback: Boolean,
    val cfAccessClientId: String,
    val cfAccessClientSecret: String,
)

@Composable
fun SettingsScreen(
    config: AegisConnectionConfig,
    onSave: (ConnectionSaveRequest) -> Unit,
    onConnect: () -> Unit,
) {
    var host by remember(config.host) { mutableStateOf(config.host) }
    var port by remember(config.port) { mutableStateOf(config.port.toString()) }
    var token by remember(config.pairingToken) { mutableStateOf(config.pairingToken) }
    AegisPanel(modifier = Modifier.padding(16.dp).fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(16.dp)) {
            Text("Connection", color = AegisText)
            Text(
                "Use Core LAN address (192.168.50.41:50051) on Wi‑Fi and cellular. " +
                    "Away from home: install Cloudflare One / WARP, join team kawaharahome, then connect.",
                color = AegisTextSecondary,
            )
            OutlinedTextField(value = host, onValueChange = { host = it }, label = { Text("Core host") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = port, onValueChange = { port = it }, label = { Text("Core port") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(
                value = token,
                onValueChange = { token = it },
                label = { Text("Pairing token") },
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth(),
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = {
                        onSave(
                            ConnectionSaveRequest(
                                host = host,
                                port = port.toIntOrNull() ?: 50051,
                                pairingToken = token,
                                fallbackHost = "",
                                fallbackPort = 50051,
                                useTlsFallback = false,
                                cfAccessClientId = "",
                                cfAccessClientSecret = "",
                            ),
                        )
                    },
                ) { Text("Save") }
                Button(onClick = onConnect) { Text("Connect") }
            }
        }
    }
}
