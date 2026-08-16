import org.gradle.api.tasks.Sync
import org.gradle.kotlin.dsl.register

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

val generatedAssetsDirectory = layout.buildDirectory.dir("generated/p00-assets")
val generatedResDirectory = layout.buildDirectory.dir("generated/p00-res")
val syncP00Assets by tasks.registering(Sync::class) {
    into(generatedAssetsDirectory)
    from("../../05_BRAND") { include("logo_wordmark_v130.png", "app_icon_1024_v130.png", "BRAND_ASSET_MANIFEST_V130.yaml"); into("brand") }
    from("../../06_MINERS/PNG_V130") { include("MINER_L01.png"); into("miners") }
    from("../../07_GAME_ASSETS/v130") {
        include("ASSET_MANIFEST_V130.json", "backgrounds/bg_secure.png", "panels/panel_regular.png", "icons/token_star_point.png", "icons/token_energy_chip.png", "icons/icon_check.png")
        into("game")
    }
    from("../../08_VFX") { include("VFX_MANIFEST.yaml", "effects/VFX_LEVEL_UNLOCK.png"); into("vfx") }
    from("../../09_AUDIO") { include("AUDIO_MANIFEST.yaml", "AUDIO_CUE_MAP.yaml", "SFX/SFX_UI_TAP.ogg"); into("audio") }
}
val syncP00BrandResources by tasks.registering(Sync::class) {
    into(generatedResDirectory)
    from("../../05_BRAND/app_icon/mdpi") { into("mipmap-mdpi") }
    from("../../05_BRAND/app_icon/hdpi") { into("mipmap-hdpi") }
    from("../../05_BRAND/app_icon/xhdpi") { into("mipmap-xhdpi") }
    from("../../05_BRAND/app_icon/xxhdpi") { into("mipmap-xxhdpi") }
    from("../../05_BRAND/app_icon/xxxhdpi") { into("mipmap-xxxhdpi") }
}

android {
    namespace = "cc.orbexa.xkjy"
    compileSdk = 35

    defaultConfig {
        applicationId = "cc.orbexa.xkjy"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.0.1-p00"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    buildFeatures { compose = true; buildConfig = true }
    sourceSets.getByName("main").assets.srcDir(generatedAssetsDirectory)
    sourceSets.getByName("main").res.srcDir(generatedResDirectory)
}

val signingStore = providers.environmentVariable("ANDROID_KEYSTORE_FILE").orNull
val signingStorePassword = providers.environmentVariable("ANDROID_KEYSTORE_PASSWORD").orNull
val signingAlias = providers.environmentVariable("ANDROID_KEY_ALIAS").orNull
val signingKeyPassword = providers.environmentVariable("ANDROID_KEY_PASSWORD").orNull
if (listOf(signingStore, signingStorePassword, signingAlias, signingKeyPassword).all { !it.isNullOrBlank() }) {
    android.signingConfigs.create("p00Release") {
        storeFile = file(signingStore!!)
        storePassword = signingStorePassword
        keyAlias = signingAlias
        keyPassword = signingKeyPassword
    }
    android.buildTypes.getByName("release").signingConfig = android.signingConfigs.getByName("p00Release")
}

tasks.named("preBuild").configure { dependsOn(syncP00Assets, syncP00BrandResources) }

dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.12.01"))
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-compose:1.10.0")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation(platform("androidx.compose:compose-bom:2024.12.01"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
}
