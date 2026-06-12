//! Health endpoint for PC Server.
//!
//! Simple TCP JSON health check that AI Server and Docker can use.
//! Protocol: Send "command\n" → receive JSON response.

use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::thread;

use crate::observe;
use crate::safety;

/// Health status response.
#[derive(serde::Serialize)]
pub struct HealthStatus {
    pub status: String,
    pub server_id: String,
    pub version: String,
    pub capabilities: usize,
    pub os_name: String,
    pub os_version: String,
    pub uptime_seconds: u64,
}

/// Overlay state (global).
static OVERLAY_ACTIVE: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
static OVERLAY_TEXT: std::sync::Mutex<String> = std::sync::Mutex::new(String::new());

static START_TIME: std::sync::OnceLock<std::time::Instant> = std::sync::OnceLock::new();

fn get_uptime() -> u64 {
    START_TIME.get_or_init(std::time::Instant::now).elapsed().as_secs()
}

fn handle_client(mut stream: TcpStream) {
    let reader = BufReader::new(stream.try_clone().unwrap());
    for line in reader.lines() {
        match line {
            Ok(cmd) => {
                let cmd = cmd.trim().to_string();
                let response = handle_command(&cmd);
                let _ = stream.write_all(format!("{}\n", response).as_bytes());
                let _ = stream.flush();
            }
            Err(_) => break,
        }
    }
}

fn handle_command(cmd: &str) -> String {
    // Parse command and optional JSON params
    let parts: Vec<&str> = cmd.splitn(2, ' ').collect();
    let command = parts[0];
    let params = parts.get(1).unwrap_or(&"{}");

    match command {
        // ── Health ──────────────────────────────────────────
        "health" => {
            let os_info = observe::get_os_info();
            let status = HealthStatus {
                status: "ok".to_string(),
                server_id: "pc-server-host".to_string(),
                version: "0.2.0".to_string(),
                capabilities: safety::get_capabilities().len(),
                os_name: os_info.os_name,
                os_version: os_info.os_version,
                uptime_seconds: get_uptime(),
            };
            serde_json::to_string(&status).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }

        // ── Observe (Level 0) ──────────────────────────────
        "screenshot" => {
            let result = observe::get_screenshot();
            serde_json::to_string(&result.unwrap()).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "active_window" => {
            let result = observe::get_active_window();
            serde_json::to_string(&result.unwrap()).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "windows" => {
            let result = observe::list_windows();
            serde_json::to_string(&result.unwrap()).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "os_info" => {
            let result = observe::get_os_info();
            serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "screen_size" => {
            let result = observe::get_screen_size();
            serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "clipboard" => {
            let result = observe::get_clipboard();
            serde_json::to_string(&result.unwrap()).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }

        // ── Overlay (Level 1) ──────────────────────────────
        "show_overlay" => {
            let text = if params.is_empty() { "AEGIS Overlay" } else { params };
            OVERLAY_ACTIVE.store(true, std::sync::atomic::Ordering::Relaxed);
            *OVERLAY_TEXT.lock().unwrap() = text.to_string();
            format!("{{\"status\":\"ok\",\"action\":\"show_overlay\",\"text\":\"{}\"}}", text)
        }
        "hide_overlay" => {
            OVERLAY_ACTIVE.store(false, std::sync::atomic::Ordering::Relaxed);
            *OVERLAY_TEXT.lock().unwrap() = String::new();
            "{\"status\":\"ok\",\"action\":\"hide_overlay\"}".to_string()
        }

        // ── App/Window (Level 1) ───────────────────────────
        "launch_app" => {
            // Mock: in real implementation, use std::process::Command
            format!("{{\"status\":\"ok\",\"action\":\"launch_app\",\"app\":\"{}\"}}", params)
        }
        "focus_window" => {
            // Mock: in real implementation, use Windows API
            format!("{{\"status\":\"ok\",\"action\":\"focus_window\",\"target\":\"{}\"}}", params)
        }

        // ── Input (Level 2: Approval required) ─────────────
        "mouse_move" => {
            // Mock: in real implementation, use Windows API
            format!("{{\"status\":\"ok\",\"action\":\"mouse_move\",\"params\":\"{}\"}}", params)
        }
        "mouse_click" => {
            // Approval required — return approval needed
            "{\"status\":\"approval_required\",\"action\":\"mouse_click\",\"reason\":\"Mouse click requires user approval\"}".to_string()
        }
        "keyboard_type" => {
            // Approval required — return approval needed
            "{\"status\":\"approval_required\",\"action\":\"keyboard_type\",\"reason\":\"Keyboard input requires user approval\"}".to_string()
        }
        "press_hotkey" => {
            // Approval required — return approval needed
            "{\"status\":\"approval_required\",\"action\":\"press_hotkey\",\"reason\":\"Hotkey requires user approval\"}".to_string()
        }

        // ── Capabilities ───────────────────────────────────
        "capabilities" => {
            let caps = safety::get_capabilities();
            serde_json::to_string(&caps).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }

        // ── Control ────────────────────────────────────────
        "quit" => {
            "{\"status\":\"ok\",\"action\":\"quit\"}".to_string()
        }

        _ => {
            format!("{{\"error\":\"unknown_command\",\"command\":\"{}\"}}", command)
        }
    }
}

/// Start the health server on the given address.
pub fn start_health_server(addr: &str) {
    let listener = TcpListener::bind(addr).expect("Failed to bind health server");
    println!("PC Server listening on {}", addr);

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                thread::spawn(move || handle_client(stream));
            }
            Err(e) => {
                eprintln!("Connection failed: {}", e);
            }
        }
    }
}
