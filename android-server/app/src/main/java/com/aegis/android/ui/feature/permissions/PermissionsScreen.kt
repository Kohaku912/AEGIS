package com.aegis.android.ui.feature.permissions

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.aegis.android.ui.designsystem.AegisPanel
import com.aegis.android.ui.designsystem.AegisText
import com.aegis.android.ui.designsystem.AegisTextSecondary
import com.aegis.android.ui.model.MobilePermissionSnapshot

@Composable
fun PermissionsScreen(snapshot: MobilePermissionSnapshot, onAction: (String) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(16.dp)) {
        PermissionRow("Notification runtime", snapshot.notificationRuntime) { onAction("notification-runtime") }
        PermissionRow("Notification access", snapshot.notificationAccess) { onAction("notification-access") }
        PermissionRow("Accessibility", snapshot.accessibility) { onAction("accessibility") }
        PermissionRow("Screenshot", snapshot.screenshot) { onAction("screenshot") }
        PermissionRow("Overlay", snapshot.overlay) { onAction("overlay") }
        PermissionRow("Location", snapshot.location) { onAction("location") }
    }
}

@Composable
private fun PermissionRow(label: String, granted: Boolean, action: () -> Unit) {
    AegisPanel(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(16.dp)) {
            Text(label, color = AegisText)
            Text(if (granted) "OK" else "Missing or not yet observed", color = AegisTextSecondary)
            if (!granted) Button(onClick = action) { Text("Open") }
        }
    }
}
