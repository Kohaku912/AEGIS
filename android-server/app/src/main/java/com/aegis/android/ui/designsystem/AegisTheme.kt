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
import androidx.compose.ui.unit.Dp

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
    diameter: Dp = 154.dp,
) {
    val statusColor = when (health.uppercase()) {
        "ONLINE" -> AegisSuccess
        "DEGRADED" -> AegisWarning
        "OFFLINE" -> AegisCritical
        else -> AegisCyan
    }
    Canvas(modifier = modifier.size(diameter)) {
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
