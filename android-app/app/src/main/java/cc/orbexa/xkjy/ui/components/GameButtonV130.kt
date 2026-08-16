package cc.orbexa.xkjy.ui.components

import androidx.compose.foundation.background
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
import cc.orbexa.xkjy.ui.theme.StarMineDimensV130
import cc.orbexa.xkjy.ui.theme.StarMineTypeV130

@Composable
fun GameButtonV130(text: String, modifier: Modifier = Modifier, enabled: Boolean = true, onClick: () -> Unit) {
    val shape = RoundedCornerShape(13.dp)
    Box(modifier = modifier.fillMaxWidth().height(StarMineDimensV130.ButtonHeight).clip(shape).background(Brush.verticalGradient(listOf(Color(0xFFFFDC65), Color(0xFFF7A834), Color(0xFFE87928)))).clickable(enabled = enabled, onClick = onClick).padding(horizontal = 18.dp), contentAlignment = Alignment.Center) {
        Text(text = text, color = Color(0xFF4C2900).copy(alpha = if (enabled) 1f else .45f), fontSize = StarMineTypeV130.Button, fontWeight = FontWeight.Black, maxLines = 1, overflow = TextOverflow.Ellipsis)
    }
}
