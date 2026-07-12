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

@Composable
fun SettingsScreen(config: AegisConnectionConfig, onSave: (String, Int, String) -> Unit, onConnect: () -> Unit) {
    var host by remember(config.host) { mutableStateOf(config.host) }
    var port by remember(config.port) { mutableStateOf(config.port.toString()) }
    var token by remember(config.pairingToken) { mutableStateOf(config.pairingToken) }
    AegisPanel(modifier = Modifier.padding(16.dp).fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(16.dp)) {
            Text("Connection", color = AegisText)
            Text("Host can be LAN, Tailscale IP, or MagicDNS.", color = AegisTextSecondary)
            OutlinedTextField(value = host, onValueChange = { host = it }, label = { Text("Host") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = port, onValueChange = { port = it }, label = { Text("Port") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = token, onValueChange = { token = it }, label = { Text("Pairing token") }, visualTransformation = PasswordVisualTransformation(), modifier = Modifier.fillMaxWidth())
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { onSave(host, port.toIntOrNull() ?: 50051, token) }) { Text("Save") }
                Button(onClick = onConnect) { Text("Connect") }
            }
        }
    }
}
