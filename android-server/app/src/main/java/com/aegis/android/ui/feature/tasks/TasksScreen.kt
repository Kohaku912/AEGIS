package com.aegis.android.ui.feature.tasks

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.aegis.android.ui.designsystem.AegisPanel
import com.aegis.android.ui.designsystem.AegisText
import com.aegis.android.ui.designsystem.AegisTextSecondary
import com.aegis.android.ui.model.UiOverviewSnapshot

@Composable
fun TasksScreen(overview: UiOverviewSnapshot) {
    AegisPanel(modifier = Modifier.padding(16.dp)) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Current Task", color = AegisText)
            Text(overview.activeTaskTitle, color = AegisTextSecondary)
            Text("Raw overview is available for future task-detail rendering.", color = AegisTextSecondary)
        }
    }
}
