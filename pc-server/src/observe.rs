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

#[derive(Debug, Serialize, Deserialize)]
pub struct ScreenSize {
    pub width: u32,
    pub height: u32,
}

// ── Mock implementations (cross-platform) ──────────────────

pub fn get_screenshot() -> Result<ScreenshotResult, String> {
    let size = get_screen_size();
    Ok(ScreenshotResult {
        width: size.width,
        height: size.height,
        image_base64: "[MOCK_SCREENSHOT]".to_string(),
        format: "png".to_string(),
        captured_at_ms: now_ms(),
    })
}

pub fn get_active_window() -> Result<WindowInfo, String> {
    Ok(WindowInfo {
        title: "AEGIS - Development".to_string(),
        process_name: "code.exe".to_string(),
        pid: 12345,
        x: 0, y: 0, width: 1920, height: 1080,
        is_minimized: false,
        is_visible: true,
    })
}

pub fn list_windows() -> Result<Vec<WindowInfo>, String> {
    Ok(vec![
        get_active_window()?,
        WindowInfo {
            title: "Chrome - AEGIS Dashboard".to_string(),
            process_name: "chrome.exe".to_string(),
            pid: 12346,
            x: 100, y: 100, width: 1200, height: 800,
            is_minimized: false,
            is_visible: true,
        },
    ])
}

pub fn get_clipboard() -> Result<String, String> {
    Ok("[MOCK_CLIPBOARD_CONTENT]".to_string())
}

pub fn get_os_info() -> OsInfo {
    OsInfo {
        os_name: std::env::consts::OS.to_string(),
        os_version: "unknown".to_string(),
        hostname: get_hostname(),
        username: get_username(),
        architecture: std::env::consts::ARCH.to_string(),
    }
}

pub fn get_screen_size() -> ScreenSize {
    ScreenSize {
        width: 1920,
        height: 1080,
    }
}

fn get_hostname() -> String {
    std::env::var("COMPUTERNAME").unwrap_or_else(|_| "localhost".to_string())
}

fn get_username() -> String {
    std::env::var("USERNAME").unwrap_or_else(|_| "user".to_string())
}

fn now_ms() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}
