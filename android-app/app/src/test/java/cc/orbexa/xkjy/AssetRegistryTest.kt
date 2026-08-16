package cc.orbexa.xkjy

import cc.orbexa.xkjy.data.AssetRegistry
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class AssetRegistryTest {
    @Test fun registeredAssetsHaveUniqueIdsAndValidPaths() {
        assertEquals(AssetRegistry.required.size, AssetRegistry.required.map { it.id }.toSet().size)
        assertTrue(AssetRegistry.required.all { it.relativePath.contains('/') && !it.relativePath.startsWith('/') })
    }
}
