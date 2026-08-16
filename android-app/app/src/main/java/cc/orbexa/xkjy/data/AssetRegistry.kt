package cc.orbexa.xkjy.data

// P00 owns all app-visible paths here so later pages do not scatter raw asset paths.
object AssetRegistry {
    data class Asset(val id: String, val relativePath: String, val kind: String)
    val required = listOf(
        Asset("BRAND_WORDMARK", "brand/logo_wordmark_v130.png", "brand"),
        Asset("TOKEN_STAR", "game/icons/token_star_point.png", "token"),
        Asset("TOKEN_ENERGY", "game/icons/token_energy_chip.png", "token"),
        Asset("ICON_CHECK", "game/icons/icon_check.png", "icon"),
        Asset("MINER_L01", "miners/MINER_L01.png", "miner"),
        Asset("PANEL_REGULAR", "game/panels/panel_regular.png", "panel"),
        Asset("VFX_LEVEL_UNLOCK", "vfx/effects/VFX_LEVEL_UNLOCK.png", "vfx"),
        Asset("SFX_UI_TAP", "audio/SFX/SFX_UI_TAP.ogg", "audio"),
    )
}
