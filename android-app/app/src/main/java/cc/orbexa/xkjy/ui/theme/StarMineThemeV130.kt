package cc.orbexa.xkjy.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

object StarMineColorsV130 {
    val Background = Color(0xFF040817)
    val BackgroundAlt = Color(0xFF071126)
    val Panel = Color(0xFF0B1733)
    val PanelEmphasis = Color(0xFF101F45)
    val Border = Color(0xFF28456F)
    val TextPrimary = Color(0xFFF4F7FF)
    val TextSecondary = Color(0xFF9EACC9)
    val Gold = Color(0xFFF6BD48)
    val Orange = Color(0xFFEF862D)
    val Blue = Color(0xFF4267E8)
    val Cyan = Color(0xFF31C9E7)
    val Success = Color(0xFF49C99C)
    val Error = Color(0xFFE95367)
}

object StarMineDimensV130 {
    val ScreenHorizontal = 14.dp
    val ButtonHeight = 42.dp
    val CardRadius = 16.dp
    val PanelRadius = 18.dp
}

object StarMineTypeV130 { val Caption = 8.sp; val Body = 11.sp; val Button = 13.sp; val Section = 15.sp; val Title = 17.sp }

@Composable
fun StarMineThemeV130(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = darkColorScheme(background = StarMineColorsV130.Background, surface = StarMineColorsV130.Panel, primary = StarMineColorsV130.Gold, onPrimary = Color(0xFF4C2900), onSurface = StarMineColorsV130.TextPrimary), content = content)
}
