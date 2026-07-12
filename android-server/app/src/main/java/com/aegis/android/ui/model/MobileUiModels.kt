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
    val generatedAtMs: Long = 0L,
    val coreMode: String = "IDLE",
    val coreHealth: String = "UNKNOWN",
    val pendingApprovals: Int = 0,
    val activeTaskTitle: String = "No active task",
)
