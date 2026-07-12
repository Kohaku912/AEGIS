package com.aegis.android.ui.feature.approvals

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.grpc.ApprovalItem
import com.aegis.android.ui.designsystem.AegisPanel
import com.aegis.android.ui.designsystem.AegisText
import com.aegis.android.ui.designsystem.AegisTextSecondary
import kotlinx.coroutines.launch

@Composable
fun ApprovalsScreen(client: AegisGrpcClient, approvals: List<ApprovalItem>, onRefresh: () -> Unit) {
    val scope = rememberCoroutineScope()
    LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxSize().padding(16.dp)) {
        if (approvals.isEmpty()) {
            item {
                AegisPanel(modifier = Modifier.fillMaxWidth()) {
                    Text("No pending approvals", color = AegisTextSecondary, modifier = Modifier.padding(16.dp))
                }
            }
        }
        items(approvals) { approval ->
            AegisPanel(modifier = Modifier.fillMaxWidth()) {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.padding(16.dp)) {
                    Text(approval.summary, color = AegisText, fontWeight = FontWeight.Bold)
                    Text(approval.capabilityId, color = AegisTextSecondary)
                    Text("Risk: ${approval.risk.ifBlank { "review required" }}", color = AegisTextSecondary)
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(onClick = { scope.launch { client.resolveApproval(approval.approvalId, true); onRefresh() } }) { Text("Approve") }
                        Button(onClick = { scope.launch { client.resolveApproval(approval.approvalId, false); onRefresh() } }) { Text("Reject") }
                    }
                }
            }
        }
    }
}
