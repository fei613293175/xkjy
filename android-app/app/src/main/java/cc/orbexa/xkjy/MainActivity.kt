package cc.orbexa.xkjy

import android.os.Bundle
import android.graphics.BitmapFactory
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.material3.OutlinedTextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import cc.orbexa.xkjy.data.AssetRegistry
import cc.orbexa.xkjy.ui.components.GameButtonV130
import cc.orbexa.xkjy.ui.theme.StarMineColorsV130
import cc.orbexa.xkjy.ui.theme.StarMineDimensV130
import cc.orbexa.xkjy.ui.theme.StarMineThemeV130
import cc.orbexa.xkjy.ui.theme.StarMineTypeV130

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { StarMineThemeV130 { P00BaselineScreen() } }
    }
}

@Composable
private fun P00BaselineScreen() {
    var lastCheck by remember { mutableStateOf("尚未发起连接检查") }
    var verificationNote by remember { mutableStateOf("") }
    LazyColumn(modifier = Modifier.fillMaxSize().background(StarMineColorsV130.Background).padding(horizontal = StarMineDimensV130.ScreenHorizontal), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item { Spacer(Modifier.height(10.dp)) }
        item {
            Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                Column { Text("星矿纪元", color = StarMineColorsV130.TextPrimary, fontSize = StarMineTypeV130.Title, fontWeight = FontWeight.Black); Text("P00 · 工程基线", color = StarMineColorsV130.TextSecondary, fontSize = StarMineTypeV130.Body) }
                Text("V1.3.0", color = StarMineColorsV130.Cyan, fontSize = StarMineTypeV130.Body, fontWeight = FontWeight.Bold)
            }
        }
        item { StatusPanel(lastCheck) }
        item { Text("已注册资源", color = StarMineColorsV130.TextPrimary, fontSize = StarMineTypeV130.Section, fontWeight = FontWeight.Bold) }
        items(AssetRegistry.required, key = { it.id }) { asset -> AssetRow(asset) }
        item {
            OutlinedTextField(
                value = verificationNote,
                onValueChange = { verificationNote = it.take(40) },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("本地验收备注") },
                supportingText = { Text("仅保留在当前页面，用于真机输入验收") },
                singleLine = true,
            )
        }
        item {
            GameButtonV130(text = "执行基础自检", onClick = {
                lastCheck = if (verificationNote.isBlank()) "资源注册表完整 · 等待服务器 API 与真机验收" else "资源注册表完整 · 备注已写入当前诊断状态"
            })
        }
        item { Text("本版本只建立 Android 工程、资源注册和诊断门禁；账号、游戏棋盘、支付与钱包功能将在对应后续版本实现。", color = StarMineColorsV130.TextSecondary, fontSize = StarMineTypeV130.Body, modifier = Modifier.padding(bottom = 28.dp)) }
    }
}

@Composable
private fun StatusPanel(lastCheck: String) {
    val shape = RoundedCornerShape(StarMineDimensV130.PanelRadius)
    Column(modifier = Modifier.fillMaxWidth().clip(shape).background(StarMineColorsV130.PanelEmphasis).border(BorderStroke(1.dp, StarMineColorsV130.Border), shape).padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) { AssetIcon("game/icons/icon_check.png", "基线已加载", Modifier.size(20.dp)); Text("Android 基线壳已加载", color = StarMineColorsV130.TextPrimary, fontWeight = FontWeight.Bold, fontSize = StarMineTypeV130.Section) }
        Text("视觉令牌：V1.3.0 · 设计基准：360 × 760dp", color = StarMineColorsV130.TextSecondary, fontSize = StarMineTypeV130.Body)
        Text(lastCheck, color = StarMineColorsV130.Cyan, fontSize = StarMineTypeV130.Body, maxLines = 2, overflow = TextOverflow.Ellipsis)
    }
}

@Composable
private fun AssetRow(asset: AssetRegistry.Asset) {
    val shape = RoundedCornerShape(StarMineDimensV130.CardRadius)
    Row(modifier = Modifier.fillMaxWidth().clip(shape).background(StarMineColorsV130.Panel).border(BorderStroke(1.dp, StarMineColorsV130.Border), shape).padding(horizontal = 14.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        AssetIcon("game/icons/icon_check.png", null, Modifier.size(18.dp))
        Column {
            Text(asset.id, color = StarMineColorsV130.TextPrimary, fontSize = StarMineTypeV130.Body, fontWeight = FontWeight.Bold)
            Text(asset.relativePath, color = StarMineColorsV130.TextSecondary, fontSize = StarMineTypeV130.Caption, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(asset.kind, color = StarMineColorsV130.Cyan, fontSize = StarMineTypeV130.Caption)
        }
    }
}

@Composable
private fun AssetIcon(path: String, description: String?, modifier: Modifier) {
    val context = LocalContext.current
    val bitmap = remember(path) {
        context.assets.open(path).use { stream ->
            requireNotNull(BitmapFactory.decodeStream(stream)) { "Unable to decode registered asset: $path" }.asImageBitmap()
        }
    }
    Image(bitmap = bitmap, contentDescription = description, modifier = modifier, contentScale = ContentScale.Fit)
}
