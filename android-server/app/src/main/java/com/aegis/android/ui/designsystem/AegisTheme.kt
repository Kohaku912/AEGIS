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
import androidx.compose.ui.graphics.Path
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
            .border(1.dp, AegisBorder, RoundedCornerShape(8.dp)),
        colors = CardDefaults.cardColors(containerColor = AegisSurface),
        shape = RoundedCornerShape(8.dp),
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
        "ONLINE" -> AegisCyan
        "DEGRADED" -> AegisWarning
        "OFFLINE" -> AegisCritical
        else -> AegisCyan
    }
    Canvas(modifier = modifier.size(diameter)) {
        val center = Offset(size.width / 2f, size.height / 2f)
        val unit = size.minDimension / 10f
        val cognition = Path().apply {
            moveTo(center.x, center.y - unit * 1.5f)
            lineTo(center.x + unit * 1.35f, center.y - unit * .72f)
            lineTo(center.x + unit * 1.35f, center.y + unit * .72f)
            lineTo(center.x, center.y + unit * 1.5f)
            lineTo(center.x - unit * 1.35f, center.y + unit * .72f)
            lineTo(center.x - unit * 1.35f, center.y - unit * .72f)
            close()
        }
        drawPath(cognition, statusColor.copy(alpha = .14f))
        drawPath(cognition, statusColor, style = Stroke(width = 3.dp.toPx()))
        val nodes = listOf(
            Offset(center.x - unit * 3.6f, center.y - unit * 2.7f),
            Offset(center.x + unit * 3.6f, center.y - unit * 2.4f),
            Offset(center.x - unit * 3.4f, center.y + unit * 2.6f),
            Offset(center.x + unit * 3.5f, center.y + unit * 2.8f),
        )
        nodes.forEachIndexed { index, node ->
            drawLine(color = if (index == 1 && mode.uppercase() == "EXECUTING") AegisAction else AegisInfrastructure, start = center, end = node, strokeWidth = if (index == 1 && mode.uppercase() == "EXECUTING") 4.dp.toPx() else 2.dp.toPx(), cap = StrokeCap.Round)
            drawRect(color = statusColor.copy(alpha = .18f), topLeft = Offset(node.x - unit * .45f, node.y - unit * .32f), size = Size(unit * .9f, unit * .64f))
            drawRect(color = statusColor, topLeft = Offset(node.x - unit * .45f, node.y - unit * .32f), size = Size(unit * .9f, unit * .64f), style = Stroke(width = 2.dp.toPx()))
        }
        val missionY = center.y + unit * 4f
        drawLine(color = AegisTextSecondary.copy(alpha = .35f), start = Offset(unit, missionY), end = Offset(size.width - unit, missionY), strokeWidth = 2.dp.toPx())
        val progress = when (mode.uppercase()) { "EXECUTING" -> .72f; "WAITING" -> .55f; "OBSERVING" -> .24f; else -> .12f }
        drawLine(color = AegisAction, start = Offset(unit, missionY), end = Offset(unit + (size.width - unit * 2f) * progress, missionY), strokeWidth = 4.dp.toPx(), cap = StrokeCap.Round)
        if (pendingApprovals > 0) {
            drawRect(color = AegisWarning, topLeft = Offset(center.x - unit * 2.15f, center.y - unit * 2.05f), size = Size(unit * 4.3f, unit * 4.1f), style = Stroke(width = 3.dp.toPx()))
        }
    }
}
