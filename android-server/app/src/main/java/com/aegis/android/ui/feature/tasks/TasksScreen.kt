package com.aegis.android.ui.feature.tasks

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.aegis.android.ui.designsystem.AegisPanel
import com.aegis.android.ui.designsystem.AegisText
import com.aegis.android.ui.designsystem.AegisTextSecondary
import com.aegis.android.ui.model.UiOverviewSnapshot

@Composable
fun TasksScreen(overview: UiOverviewSnapshot) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(16.dp)) {
        AegisPanel(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(16.dp)) {
                Text("Current Task", color = AegisText, fontWeight = FontWeight.Bold)
                Text(overview.activeTaskTitle, color = AegisTextSecondary)
                Text("Phase ${overview.taskPhase} / Mission ${overview.missionPhase}", color = AegisTextSecondary)
                Text("Current action: ${overview.currentAction.ifBlank { "Not reported" }}", color = AegisTextSecondary)
                Text("Next action: ${overview.nextAction.ifBlank { "Not reported" }}", color = AegisTextSecondary)
                if (overview.blockedReason.isNotBlank()) {
                    Text("Blocked: ${overview.blockedReason}", color = AegisTextSecondary)
                }
            }
        }
        AegisPanel(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(16.dp)) {
                Text("Task Buckets", color = AegisText, fontWeight = FontWeight.Bold)
                Text("Active ${overview.activeTaskCount} / Waiting ${overview.waitingTaskCount} / Scheduled ${overview.scheduledTaskCount}", color = AegisTextSecondary)
                Text("Active goal: ${overview.activeGoal}", color = AegisTextSecondary)
            }
        }
    }
}
