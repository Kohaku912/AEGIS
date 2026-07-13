package com.aegis.android.ui.designsystem

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.aegis.android.grpc.ApprovalItem
import com.aegis.android.ui.model.UiServerSummary
import java.text.DateFormat
import java.util.Date

@Composable
fun AegisStatusChip(
    label: String,
    status: String,
    modifier: Modifier = Modifier,
) {
    val color = statusColor(status)
    Row(
        modifier = modifier
            .border(1.dp, color.copy(alpha = 0.45f), RoundedCornerShape(999.dp))
            .background(color.copy(alpha = 0.10f), RoundedCornerShape(999.dp))
            .padding(horizontal = 10.dp, vertical = 5.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, color = AegisTextSecondary)
        Text(status.ifBlank { "Not reported" }, color = color, fontWeight = FontWeight.Bold)
    }
}

@Composable
fun FreshnessLabel(stale: Boolean, generatedAtMs: Long = 0L) {
    val label = if (stale) "Stale" else "Fresh"
    val suffix = if (generatedAtMs > 0L) " / ${formatTime(generatedAtMs)}" else ""
    Text("$label$suffix", color = if (stale) AegisWarning else AegisTextSecondary)
}

@Composable
fun EmptyState(title: String, body: String, modifier: Modifier = Modifier) {
    AegisPanel(modifier = modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(16.dp)) {
            Text(title, color = AegisText, fontWeight = FontWeight.Bold)
            Text(body, color = AegisTextSecondary)
        }
    }
}

@Composable
fun PermissionMissingState(missing: List<String>, modifier: Modifier = Modifier) {
    AegisPanel(modifier = modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(16.dp)) {
            Text("Permission missing", color = AegisWarning, fontWeight = FontWeight.Bold)
            Text(missing.joinToString(", ").ifBlank { "No missing permission reported" }, color = AegisTextSecondary)
        }
    }
}

@Composable
fun TaskProgressBlock(
    title: String,
    phase: String,
    currentAction: String,
    nextAction: String,
    modifier: Modifier = Modifier,
) {
    AegisPanel(modifier = modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(16.dp)) {
            Text(title.ifBlank { "No active task" }, color = AegisText, fontWeight = FontWeight.Bold)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                AegisStatusChip("Phase", phase.ifBlank { "Not reported" })
            }
            Text("Now: ${currentAction.ifBlank { "Standing by" }}", color = AegisTextSecondary)
            Text("Next: ${nextAction.ifBlank { "Not reported" }}", color = AegisTextSecondary)
        }
    }
}

@Composable
fun ServerStatusRow(server: UiServerSummary, modifier: Modifier = Modifier) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .border(1.dp, AegisBorder, RoundedCornerShape(10.dp))
            .background(AegisSurfaceElevated, RoundedCornerShape(10.dp))
            .padding(12.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(server.label.ifBlank { server.serverId }, color = AegisText, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
        AegisStatusChip("", server.status.ifBlank { "Unknown" })
    }
    if (server.detail.isNotBlank()) {
        Text(server.detail, color = AegisTextSecondary, modifier = Modifier.padding(horizontal = 12.dp, vertical = 3.dp))
    }
}

@Composable
fun ApprovalRiskCard(
    approval: ApprovalItem,
    approving: Boolean,
    onApprove: () -> Unit,
    onReject: () -> Unit,
    modifier: Modifier = Modifier,
) {
    AegisPanel(modifier = modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.padding(16.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                Text(
                    approval.summary.ifBlank { approval.requestedAction.ifBlank { "Approval required" } },
                    color = AegisText,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f),
                )
                AegisStatusChip("Risk", approval.risk.ifBlank { "review" })
            }
            ApprovalLine("Approval ID", approval.approvalId)
            ApprovalLine("Target", approval.target.ifBlank { "Not specified" })
            ApprovalLine("Capability", approval.capabilityId)
            ApprovalLine("Reason", approval.reason.ifBlank { "No additional reason reported" })
            ApprovalLine("Preview", approval.preview.ifBlank { "No preview reported" })
            ApprovalLine("Task", approval.taskId.ifBlank { "Not linked" })
            ApprovalLine("Status", approval.status.ifBlank { "pending" })
            ApprovalLine("Expires", formatTime(approval.expiresAtMs))
            Spacer(modifier = Modifier.height(2.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = onApprove, enabled = !approving) { Text(if (approving) "Approving" else "Approve") }
                OutlinedButton(onClick = onReject, enabled = !approving) { Text("Reject") }
            }
        }
    }
}

@Composable
private fun ApprovalLine(label: String, value: String) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(label, color = AegisTextSecondary, fontWeight = FontWeight.Bold)
        Text(value.ifBlank { "Not reported" }, color = AegisText)
    }
}

private fun statusColor(status: String): Color = when (status.uppercase()) {
    "ONLINE", "OK", "FRESH" -> AegisCyan
    "DEGRADED", "WAITING", "MISSING", "STALE", "REVIEW" -> AegisWarning
    "OFFLINE", "CRITICAL", "FAILED", "ERROR" -> AegisCritical
    else -> AegisTextSecondary
}

private fun formatTime(value: Long): String {
    if (value <= 0L) return "Not reported"
    return DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT).format(Date(value))
}
