package com.aegis.android.ui

import com.aegis.android.ui.model.UiOverviewSnapshot
import com.aegis.android.ui.model.UiServerSummary
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AegisMobileUiModelTest {
    @Test
    fun overviewDefaultsAreUserFacing() {
        val snapshot = UiOverviewSnapshot()

        assertEquals("IDLE", snapshot.coreMode)
        assertEquals("Idle", snapshot.missionPhase)
        assertEquals("No active task", snapshot.activeTaskTitle)
        assertEquals("No data yet", snapshot.activeGoal)
        assertFalse(snapshot.freshnessStale)
    }

    @Test
    fun serverSummaryCarriesStatusAndHeartbeat() {
        val server = UiServerSummary(
            serverId = "android-server",
            label = "Android",
            status = "ONLINE",
            mode = "reverse_stream",
            heartbeatAgeSeconds = 4L,
        )

        assertEquals("android-server", server.serverId)
        assertEquals("Android", server.label)
        assertTrue(server.heartbeatAgeSeconds >= 0L)
    }

    @Test
    fun navigationUsesBottomBarForPhoneWidths() {
        assertEquals(MobileNavigationMode.BOTTOM, mobileNavigationMode(360))
        assertEquals(MobileNavigationMode.BOTTOM, mobileNavigationMode(599))
    }

    @Test
    fun navigationUsesRailForTabletWidths() {
        assertEquals(MobileNavigationMode.RAIL, mobileNavigationMode(600))
        assertEquals(MobileNavigationMode.RAIL, mobileNavigationMode(840))
    }

    @Test
    fun navigationFallsBackToBottomAtTwoHundredPercentFontScale() {
        assertEquals(MobileNavigationMode.BOTTOM, mobileNavigationMode(840, 2f))
    }
}
