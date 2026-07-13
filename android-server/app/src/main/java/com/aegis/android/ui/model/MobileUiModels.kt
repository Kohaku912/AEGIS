package com.aegis.android.ui.model

data class MobilePermissionSnapshot(
    val notificationRuntime: Boolean = false,
    val notificationAccess: Boolean = false,
    val accessibility: Boolean = false,
    val screenshot: Boolean = false,
    val overlay: Boolean = false,
    val location: Boolean = false,
)

data class UiOverviewSnapshot(
    val rawJson: String = "",
    val schemaVersion: String = "",
    val generatedAtMs: Long = 0L,
    val coreMode: String = "IDLE",
    val coreHealth: String = "UNKNOWN",
    val missionPhase: String = "Idle",
    val connectionQuality: String = "Not reported",
    val freshnessStale: Boolean = false,
    val pendingApprovals: Int = 0,
    val attentionCount: Int = 0,
    val unreadNotifications: Int = 0,
    val activeGoal: String = "Not reported",
    val activeTaskTitle: String = "No active task",
    val taskPhase: String = "Not reported",
    val currentAction: String = "",
    val nextAction: String = "",
    val blockedReason: String = "",
    val activeTaskCount: Int = 0,
    val waitingTaskCount: Int = 0,
    val scheduledTaskCount: Int = 0,
    val memorySummary: String = "Not reported",
    val lastConsolidation: String = "Not reported",
    val servers: List<UiServerSummary> = emptyList(),
)

data class UiServerSummary(
    val serverId: String,
    val label: String,
    val status: String,
    val mode: String = "",
    val detail: String = "",
    val heartbeatAgeSeconds: Long = -1L,
)
