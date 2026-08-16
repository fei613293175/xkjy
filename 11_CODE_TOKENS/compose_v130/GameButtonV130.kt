package cc.orbexa.xkjy.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import cc.orbexa.xkjy.ui.theme.StarMineColorsV130
import cc.orbexa.xkjy.ui.theme.StarMineDimensV130
import cc.orbexa.xkjy.ui.theme.StarMineTypeV130

enum class GameButtonStyleV130 { PRIMARY, SECONDARY, PURPLE, DANGER, DARK }

@Composable
fun GameButtonV130(
    text: String,
    modifier: Modifier = Modifier,
    style: GameButtonStyleV130 = GameButtonStyleV130.PRIMARY,
    enabled: Boolean = true,
    onClick: () -> Unit,
) {
    val gradient = when (style) {
        GameButtonStyleV130.PRIMARY -> Brush.verticalGradient(listOf(Color(0xFFFFDC65), Color(0xFFF7A834), Color(0xFFE87928)))
        GameButtonStyleV130.SECONDARY -> Brush.verticalGradient(listOf(Color(0xFF526FF3), Color(0xFF3447BA)))
        GameButtonStyleV130.PURPLE -> Brush.verticalGradient(listOf(Color(0xFF8656ED), Color(0xFF5631BB)))
        GameButtonStyleV130.DANGER -> Brush.verticalGradient(listOf(Color(0xFFF16B78), Color(0xFFC73A52)))
        GameButtonStyleV130.DARK -> Brush.verticalGradient(listOf(Color(0xFF111E42), Color(0xFF0A142E)))
    }
    val textColor = if (style == GameButtonStyleV130.PRIMARY) Color(0xFF4C2900) else StarMineColorsV130.TextPrimary
    val shape = RoundedCornerShape(13.dp)
    Box(
        modifier = modifier
            .height(StarMineDimensV130.ButtonHeight)
            .clip(shape)
            .background(gradient)
            .border(BorderStroke(1.dp, if (style == GameButtonStyleV130.PRIMARY) Color(0xFFFFE58A) else StarMineColorsV130.Border), shape)
            .clickable(enabled = enabled, onClick = onClick)
            .padding(horizontal = 18.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = text,
            color = textColor.copy(alpha = if (enabled) 1f else .45f),
            fontSize = StarMineTypeV130.Button,
            fontWeight = FontWeight.Black,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
    }
}
