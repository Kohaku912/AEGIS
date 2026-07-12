package com.aegis.android.ui.designsystem

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp

val AegisBackground = Color(0xFF05090F)
val AegisSurface = Color(0xFF0B111B)
val AegisSurfaceElevated = Color(0xFF111A27)
val AegisBorder = Color(0xFF1E2A3A)
val AegisText = Color(0xFFEAF2FF)
val AegisTextSecondary = Color(0xFF8EA0B8)
val AegisCyan = Color(0xFF29D3FF)
val AegisViolet = Color(0xFF8B7CFF)
val AegisSuccess = Color(0xFF2DD4A8)
val AegisWarning = Color(0xFFFFB84D)
val AegisCritical = Color(0xFFFF5D73)
val AegisOffline = Color(0xFF7C8798)

private val AegisScheme = darkColorScheme(
    background = AegisBackground,
    surface = AegisSurface,
    primary = AegisCyan,
    secondary = AegisViolet,
    error = AegisCritical,
    onBackground = AegisText,
    onSurface = AegisText,
    onPrimary = AegisBackground,
)

@Composable
fun AegisTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = AegisScheme, content = content)
}

@Composable
fun AegisPanel(modifier: Modifier = Modifier, content: @Composable BoxScope.() -> Unit) {
    Card(
        modifier = modifier
            .border(1.dp, AegisBorder, RoundedCornerShape(12.dp)),
        colors = CardDefaults.cardColors(containerColor = AegisSurface),
        shape = RoundedCornerShape(12.dp),
    ) {
        Box(modifier = Modifier.background(AegisSurface), content = content)
    }
}

@Composable
fun CoreGlyph(
    mode: String,
    health: String,
    pendingApprovals: Int,
    modifier: Modifier = Modifier,
) {
    val statusColor = when (health.uppercase()) {
        "ONLINE" -> AegisSuccess
        "DEGRADED" -> AegisWarning
        "OFFLINE" -> AegisCritical
        else -> AegisCyan
    }
    Canvas(modifier = modifier.size(154.dp)) {
        val center = Offset(size.width / 2f, size.height / 2f)
        val radius = size.minDimension * 0.25f
        drawCircle(color = statusColor.copy(alpha = 0.16f), radius = radius * 1.55f, center = center)
        drawCircle(color = statusColor, radius = radius, center = center, style = Stroke(width = 4.dp.toPx()))
        drawArc(
            color = AegisViolet,
            startAngle = -90f,
            sweepAngle = when (mode.uppercase()) {
                "EXECUTING" -> 270f
                "WAITING" -> 210f
                "OBSERVING" -> 150f
                else -> 90f
            },
            useCenter = false,
            topLeft = Offset(center.x - radius * 1.45f, center.y - radius * 1.45f),
            size = Size(radius * 2.9f, radius * 2.9f),
            style = Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round),
        )
        if (pendingApprovals > 0) {
            drawArc(
                color = AegisWarning,
                startAngle = 20f,
                sweepAngle = 320f,
                useCenter = false,
                topLeft = Offset(center.x - radius * 1.85f, center.y - radius * 1.85f),
                size = Size(radius * 3.7f, radius * 3.7f),
                style = Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round),
            )
        }
    }
}
