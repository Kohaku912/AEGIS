//! Observe capabilities for PC Server — real implementations.
//!
//! Uses:
//! - `screenshots` crate for screen capture
//! - `sysinfo` crate for OS info
//! - `x-win` crate for window info
//! - `arboard` crate for clipboard

use base64::Engine;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
#[cfg(target_os = "windows")]
use std::sync::Mutex;

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

#[derive(Debug, Serialize, Deserialize)]
pub struct UserActivitySnapshot {
    pub timestamp_ms: u64,
    pub active_window_title: String,
    pub app_name: String,
    pub process_name: String,
    pub pid: u32,
    pub browser_domain: String,
    pub browser_url_hash: String,
    pub keyboard_count: u32,
    pub mouse_count: u32,
    pub key_event_count: u32,
    pub key_category_counts: BTreeMap<String, u32>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub keys: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub mouse_buttons: Vec<String>,
    pub cursor_x: i32,
    pub cursor_y: i32,
    pub input_target_category: String,
    pub idle_ms: u64,
    pub locked: bool,
    pub fullscreen: bool,
}

#[cfg(target_os = "windows")]
static INPUT_COUNTER_LOCK: Mutex<()> = Mutex::new(());

// ═══════════════════════════════════════════════════════════
// Screenshot — screenshots crate
// ═══════════════════════════════════════════════════════════

pub fn get_screenshot() -> Result<ScreenshotResult, String> {
    use screenshots::Screen;

    let screens = Screen::all().map_err(|e| format!("Failed to get screens: {e}"))?;
    let screen = screens.first().ok_or("No screens found")?;
    let image = screen
        .capture()
        .map_err(|e| format!("Failed to capture: {e}"))?;

    let buffer = encode_bmp(image.rgba(), image.width(), image.height())?;

    Ok(ScreenshotResult {
        width: image.width(),
        height: image.height(),
        image_base64: base64::engine::general_purpose::STANDARD.encode(&buffer),
        format: "bmp".into(),
        captured_at_ms: now_ms(),
    })
}

fn encode_bmp(rgba: &[u8], width: u32, height: u32) -> Result<Vec<u8>, String> {
    let row_size = width as usize * 3;
    let padding = (4 - (row_size % 4)) % 4;
    let padded_row = row_size + padding;
    let img_size = padded_row * height as usize;
    let file_size = 54 + img_size;

    let mut bmp = Vec::with_capacity(file_size);
    bmp.extend_from_slice(b"BM");
    bmp.extend_from_slice(&(file_size as u32).to_le_bytes());
    bmp.extend_from_slice(&[0u8; 4]);
    bmp.extend_from_slice(&54u32.to_le_bytes());
    bmp.extend_from_slice(&40u32.to_le_bytes());
    bmp.extend_from_slice(&(width as i32).to_le_bytes());
    bmp.extend_from_slice(&(-(height as i32)).to_le_bytes());
    bmp.extend_from_slice(&1u16.to_le_bytes());
    bmp.extend_from_slice(&24u16.to_le_bytes());
    bmp.extend_from_slice(&[0u8; 24]);

    for y in 0..height as usize {
        for x in 0..width as usize {
            let i = (y * width as usize + x) * 4;
            bmp.push(rgba[i + 2]);
            bmp.push(rgba[i + 1]);
            bmp.push(rgba[i]);
        }
        bmp.extend(std::iter::repeat_n(0u8, padding));
    }
    Ok(bmp)
}

// ═══════════════════════════════════════════════════════════
// Active Window — x-win crate
// ═══════════════════════════════════════════════════════════

pub fn get_active_window() -> Result<WindowInfo, String> {
    let window = x_win::get_active_window().map_err(|e| format!("Failed to get window: {e}"))?;
    Ok(WindowInfo {
        title: window.title,
        process_name: window.info.exec_name,
        pid: window.info.process_id,
        x: window.position.x,
        y: window.position.y,
        width: window.position.width as u32,
        height: window.position.height as u32,
        is_minimized: false,
        is_visible: true,
    })
}

pub fn get_user_activity_snapshot() -> Result<UserActivitySnapshot, String> {
    let active = get_active_window()?;
    let screen = get_screen_size();
    let fullscreen = active.x <= 0
        && active.y <= 0
        && active.width >= screen.width.saturating_sub(8)
        && active.height >= screen.height.saturating_sub(8);
    let input = get_input_transition_counts();
    let (cursor_x, cursor_y) = get_cursor_pos();
    let app_name = app_name_from_process(&active.process_name);
    let input_target_category =
        input_target_category(&active.process_name, &active.title, fullscreen);
    Ok(UserActivitySnapshot {
        timestamp_ms: now_ms(),
        active_window_title: active.title,
        app_name,
        process_name: active.process_name,
        pid: active.pid,
        browser_domain: String::new(),
        browser_url_hash: String::new(),
        keyboard_count: input.keyboard_count,
        mouse_count: input.mouse_count,
        key_event_count: input.keyboard_count.saturating_add(input.mouse_count),
        key_category_counts: input.key_category_counts,
        keys: input.keys,
        mouse_buttons: input.mouse_buttons,
        cursor_x,
        cursor_y,
        input_target_category,
        idle_ms: get_idle_ms(),
        locked: false,
        fullscreen,
    })
}

struct InputTransitions {
    keyboard_count: u32,
    mouse_count: u32,
    key_category_counts: BTreeMap<String, u32>,
    keys: Vec<String>,
    mouse_buttons: Vec<String>,
}

#[cfg(target_os = "windows")]
fn get_input_transition_counts() -> InputTransitions {
    use windows_sys::Win32::UI::Input::KeyboardAndMouse::{
        GetAsyncKeyState, VK_LBUTTON, VK_MBUTTON, VK_RBUTTON, VK_XBUTTON1, VK_XBUTTON2,
    };

    let _guard = INPUT_COUNTER_LOCK.lock().ok();
    let mouse_keys = [
        VK_LBUTTON as i32,
        VK_RBUTTON as i32,
        VK_MBUTTON as i32,
        VK_XBUTTON1 as i32,
        VK_XBUTTON2 as i32,
    ];
    let mut keyboard_count = 0u32;
    let mut mouse_count = 0u32;
    let mut category_counts = empty_key_category_counts();
    let mut keys = Vec::new();
    let mut mouse_buttons = Vec::new();

    unsafe {
        for vk in 1..=254 {
            let state = GetAsyncKeyState(vk);
            if state & 0x0001 == 0 {
                continue;
            }
            let category = key_category(vk);
            increment_category(&mut category_counts, category);
            if mouse_keys.contains(&vk) {
                mouse_count = mouse_count.saturating_add(1);
                mouse_buttons.push(key_name(vk));
            } else {
                keyboard_count = keyboard_count.saturating_add(1);
                keys.push(key_name(vk));
            }
        }
    }
    InputTransitions {
        keyboard_count,
        mouse_count,
        key_category_counts: category_counts,
        keys,
        mouse_buttons,
    }
}

#[cfg(not(target_os = "windows"))]
fn get_input_transition_counts() -> InputTransitions {
    InputTransitions {
        keyboard_count: 0,
        mouse_count: 0,
        key_category_counts: empty_key_category_counts(),
        keys: Vec::new(),
        mouse_buttons: Vec::new(),
    }
}

#[cfg(target_os = "windows")]
fn get_cursor_pos() -> (i32, i32) {
    use windows_sys::Win32::Foundation::POINT;
    use windows_sys::Win32::UI::WindowsAndMessaging::GetCursorPos;
    let mut point = POINT { x: 0, y: 0 };
    let ok = unsafe { GetCursorPos(&mut point) };
    if ok == 0 {
        (0, 0)
    } else {
        (point.x, point.y)
    }
}

#[cfg(not(target_os = "windows"))]
fn get_cursor_pos() -> (i32, i32) {
    (0, 0)
}

pub(crate) fn key_name(vk: i32) -> String {
    match vk {
        0x01 => "LButton".into(),
        0x02 => "RButton".into(),
        0x04 => "MButton".into(),
        0x05 => "XButton1".into(),
        0x06 => "XButton2".into(),
        0x08 => "Backspace".into(),
        0x09 => "Tab".into(),
        0x0D => "Enter".into(),
        0x10 => "Shift".into(),
        0x11 => "Ctrl".into(),
        0x12 => "Alt".into(),
        0x13 => "Pause".into(),
        0x14 => "CapsLock".into(),
        0x1B => "Esc".into(),
        0x20 => "Space".into(),
        0x21 => "PageUp".into(),
        0x22 => "PageDown".into(),
        0x23 => "End".into(),
        0x24 => "Home".into(),
        0x25 => "Left".into(),
        0x26 => "Up".into(),
        0x27 => "Right".into(),
        0x28 => "Down".into(),
        0x2C => "PrintScreen".into(),
        0x2D => "Insert".into(),
        0x2E => "Delete".into(),
        0x5B => "LWin".into(),
        0x5C => "RWin".into(),
        0x5D => "App".into(),
        0x70..=0x87 => format!("F{}", vk - 0x6F),
        0x90 => "NumLock".into(),
        0x91 => "ScrollLock".into(),
        0xA0 => "LShift".into(),
        0xA1 => "RShift".into(),
        0xA2 => "LCtrl".into(),
        0xA3 => "RCtrl".into(),
        0xA4 => "LAlt".into(),
        0xA5 => "RAlt".into(),
        0xBA => ";".into(),
        0xBB => "=".into(),
        0xBC => ",".into(),
        0xBD => "-".into(),
        0xBE => ".".into(),
        0xBF => "/".into(),
        0xC0 => "`".into(),
        0xDB => "[".into(),
        0xDC => "\\".into(),
        0xDD => "]".into(),
        0xDE => "'".into(),
        0x30..=0x39 => ((b'0' + (vk - 0x30) as u8) as char).to_string(),
        0x41..=0x5A => ((b'A' + (vk - 0x41) as u8) as char).to_string(),
        0x60..=0x69 => format!("Num{}", vk - 0x60),
        0x6A => "Num*".into(),
        0x6B => "Num+".into(),
        0x6D => "Num-".into(),
        0x6E => "Num.".into(),
        0x6F => "Num/".into(),
        _ => format!("VK_{vk:02X}"),
    }
}

fn empty_key_category_counts() -> BTreeMap<String, u32> {
    [
        "printable",
        "navigation",
        "editing",
        "function",
        "modifier",
        "system",
        "mouse",
    ]
    .into_iter()
    .map(|key| (key.to_string(), 0))
    .collect()
}

fn increment_category(counts: &mut BTreeMap<String, u32>, category: &'static str) {
    let value = counts.entry(category.to_string()).or_insert(0);
    *value = value.saturating_add(1);
}

fn key_category(vk: i32) -> &'static str {
    match vk {
        0x01 | 0x02 | 0x04 | 0x05 | 0x06 => "mouse",
        0x21..=0x28 => "navigation",
        0x08 | 0x09 | 0x0D | 0x2D | 0x2E => "editing",
        0x70..=0x87 => "function",
        0x10..=0x14 | 0x5B..=0x5C => "modifier",
        0x20 | 0x30..=0x5A | 0x60..=0x6F | 0xBA..=0xDE => "printable",
        _ => "system",
    }
}

fn app_name_from_process(process_name: &str) -> String {
    let trimmed = process_name.trim();
    if trimmed.is_empty() {
        return "Unknown".into();
    }
    let without_ext = trimmed
        .strip_suffix(".exe")
        .or_else(|| trimmed.strip_suffix(".EXE"))
        .unwrap_or(trimmed);
    without_ext.replace(['_', '-'], " ")
}

fn input_target_category(process_name: &str, title: &str, fullscreen: bool) -> String {
    let text = format!("{} {}", process_name, title).to_lowercase();
    if text.contains("code")
        || text.contains("devenv")
        || text.contains("jetbrains")
        || text.contains("terminal")
    {
        "coding".into()
    } else if text.contains("steam")
        || text.contains("game")
        || text.contains("minecraft")
        || text.contains("elden")
        || fullscreen
    {
        "game".into()
    } else if text.contains("chrome")
        || text.contains("edge")
        || text.contains("firefox")
        || text.contains("browser")
    {
        "browser".into()
    } else if text.contains("discord") || text.contains("line") || text.contains("slack") {
        "chat".into()
    } else {
        "application".into()
    }
}

#[cfg(target_os = "windows")]
fn get_idle_ms() -> u64 {
    use windows_sys::Win32::System::SystemInformation::GetTickCount64;
    use windows_sys::Win32::UI::Input::KeyboardAndMouse::{GetLastInputInfo, LASTINPUTINFO};

    unsafe {
        let mut info = LASTINPUTINFO {
            cbSize: std::mem::size_of::<LASTINPUTINFO>() as u32,
            dwTime: 0,
        };
        if GetLastInputInfo(&mut info) == 0 {
            return 0;
        }
        GetTickCount64().saturating_sub(info.dwTime as u64)
    }
}

#[cfg(not(target_os = "windows"))]
fn get_idle_ms() -> u64 {
    0
}

// ═══════════════════════════════════════════════════════════
// Window List — x-win crate
// ═══════════════════════════════════════════════════════════

pub fn list_windows() -> Result<Vec<WindowInfo>, String> {
    let windows = x_win::get_open_windows().map_err(|e| format!("Failed to list windows: {e}"))?;
    Ok(windows
        .into_iter()
        .map(|w| WindowInfo {
            title: w.title,
            process_name: w.info.exec_name,
            pid: w.info.process_id,
            x: w.position.x,
            y: w.position.y,
            width: w.position.width as u32,
            height: w.position.height as u32,
            is_minimized: false,
            is_visible: true,
        })
        .collect())
}

// ═══════════════════════════════════════════════════════════
// Clipboard — arboard crate
// ═══════════════════════════════════════════════════════════

pub fn get_clipboard() -> Result<String, String> {
    let mut clipboard =
        arboard::Clipboard::new().map_err(|e| format!("Failed to access clipboard: {e}"))?;
    let text = clipboard
        .get_text()
        .map_err(|e| format!("Failed to read clipboard: {e}"))?;
    Ok(if text.is_empty() {
        "[EMPTY]".into()
    } else {
        crate::redaction::redact_secrets(&text)
    })
}

// ═══════════════════════════════════════════════════════════
// OS Info — sysinfo crate
// ═══════════════════════════════════════════════════════════

pub fn get_os_info() -> OsInfo {
    use sysinfo::System;
    OsInfo {
        os_name: System::name().unwrap_or_else(|| "Unknown".into()),
        os_version: System::os_version().unwrap_or_else(|| "Unknown".into()),
        hostname: System::host_name().unwrap_or_else(|| "localhost".into()),
        username: std::env::var("USERNAME").unwrap_or_else(|_| "user".into()),
        architecture: std::env::consts::ARCH.into(),
    }
}

// ═══════════════════════════════════════════════════════════
// Screen Size — screenshots crate
// ═══════════════════════════════════════════════════════════

pub fn get_screen_size() -> ScreenSize {
    use screenshots::Screen;
    if let Ok(screens) = Screen::all() {
        if let Some(screen) = screens.first() {
            return ScreenSize {
                width: screen.display_info.width,
                height: screen.display_info.height,
            };
        }
    }
    ScreenSize {
        width: 1920,
        height: 1080,
    }
}

// ═══════════════════════════════════════════════════════════

fn now_ms() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn key_category_groups_without_key_identity() {
        assert_eq!(key_category(0x41), "printable");
        assert_eq!(key_category(0x25), "navigation");
        assert_eq!(key_category(0x08), "editing");
        assert_eq!(key_category(0x70), "function");
        assert_eq!(key_category(0x10), "modifier");
        assert_eq!(key_category(0x01), "mouse");
        assert_eq!(key_category(0x2C), "system");
    }

    #[test]
    fn key_name_maps_common_virtual_keys() {
        assert_eq!(key_name(0x41), "A");
        assert_eq!(key_name(0x0D), "Enter");
        assert_eq!(key_name(0x01), "LButton");
        assert_eq!(key_name(0x70), "F1");
        assert_eq!(key_name(0x25), "Left");
    }

    #[test]
    fn app_and_input_target_are_safe_summaries() {
        assert_eq!(app_name_from_process("eldenring.exe"), "eldenring");
        assert_eq!(
            input_target_category("eldenring.exe", "ELDEN RING", true),
            "game"
        );
        assert_eq!(
            input_target_category("Code.exe", "AEGIS - Visual Studio Code", false),
            "coding"
        );
        assert_eq!(
            input_target_category("chrome.exe", "Example", false),
            "browser"
        );
    }

    #[test]
    fn empty_counts_include_only_categories() {
        let counts = empty_key_category_counts();
        let keys: Vec<&str> = counts.keys().map(String::as_str).collect();
        assert_eq!(
            keys,
            vec![
                "editing",
                "function",
                "modifier",
                "mouse",
                "navigation",
                "printable",
                "system"
            ]
        );
        assert!(counts.values().all(|value| *value == 0));
    }
}
