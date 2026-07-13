package com.aegis.android.ui.feature.approvals

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.aegis.android.grpc.AegisGrpcClient
import com.aegis.android.grpc.ApprovalItem
import com.aegis.android.ui.designsystem.ApprovalRiskCard
import com.aegis.android.ui.designsystem.EmptyState
import kotlinx.coroutines.launch

@Composable
fun ApprovalsScreen(client: AegisGrpcClient, approvals: List<ApprovalItem>, onRefresh: () -> Unit) {
    val scope = rememberCoroutineScope()
    var busyApprovalId by remember { mutableStateOf("") }
    LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxSize().padding(16.dp)) {
        if (approvals.isEmpty()) {
            item {
                EmptyState(
                    title = "No pending approvals",
                    body = "Actions that need explicit confirmation will appear here with risk, target, preview, task, and expiration.",
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }
        items(approvals) { approval ->
            ApprovalRiskCard(
                approval = approval,
                approving = busyApprovalId == approval.approvalId,
                onApprove = {
                    scope.launch {
                        busyApprovalId = approval.approvalId
                        client.resolveApproval(approval.approvalId, true)
                        busyApprovalId = ""
                        onRefresh()
                    }
                },
                onReject = {
                    scope.launch {
                        busyApprovalId = approval.approvalId
                        client.resolveApproval(approval.approvalId, false)
                        busyApprovalId = ""
                        onRefresh()
                    }
                },
            )
        }
    }
}
