//! Observe capabilities for PC Server — read-only system observation.
//!
//! Provides mock implementations for testing cross-platform.
//! Real implementations are gated behind OS-specific feature flags.

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct ScreenshotResult {
    pub width: u32,
    pub height: u32,
    pub image_base64: String,
    pub format: String,
    pub captured_at_ms: u64,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct WindowInfo {
    pub title: String,
    pub process_name: String,
    pub pid: u32,
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
    pub is_minimized: bool,
    pub is_visible: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OsInfo {
    pub os_name: String,
    pub os_version: String,
    pub hostname: String,
    pub username: String,
    pub architecture: String,
}

// ── Mock implementations (cross-platform) ──────────────────

pub fn get_screenshot() -> Result<ScreenshotResult, String> {
    Ok(ScreenshotResult {
        width: 1920,
        height: 1080,
        image_base64: "[MOCK_SCREENSHOT]".to_string(),
        format: "png".to_string(),
        captured_at_ms: now_ms(),
    })
}

pub fn get_active_window() -> Result<WindowInfo, String> {
    Ok(WindowInfo {
        title: "Mock Window".to_string(),
        process_name: "mock.exe".to_string(),
        pid: 12345,
        x: 0, y: 0, width: 1920, height: 1080,
        is_minimized: false,
        is_visible: true,
    })
}

pub fn list_windows() -> Result<Vec<WindowInfo>, String> {
    Ok(vec![get_active_window()?])
}

pub fn get_clipboard() -> Result<String, String> {
    Ok("[MOCK_CLIPBOARD_CONTENT]".to_string())
}

pub fn get_os_info() -> OsInfo {
    OsInfo {
        os_name: std::env::consts::OS.to_string(),
        os_version: "unknown".to_string(),
        hostname: "localhost".to_string(),
        username: "user".to_string(),
        architecture: std::env::consts::ARCH.to_string(),
    }
}

fn now_ms() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}
