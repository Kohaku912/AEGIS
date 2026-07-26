//! Health endpoint for PC Server.
//!
//! Simple TCP JSON health check that AI Server and Docker can use.
//! Protocol: Send "command\n" → receive JSON response.

use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::thread;

use crate::action;
use crate::discord_rpc;
use crate::observe;
use crate::observe_ext;
use crate::overlay_approval;
use crate::safety;
use crate::system_ops;

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
    START_TIME
        .get_or_init(std::time::Instant::now)
        .elapsed()
        .as_secs()
}

fn json_response<T: ?Sized + serde::Serialize>(value: &T) -> String {
    serde_json::to_string(value).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
}

fn json_error(message: impl Into<String>) -> String {
    json_response(&serde_json::json!({ "error": message.into() }))
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
            json_response(&status)
        }

        // ── Observe (Level 0) ──────────────────────────────
        "screenshot" => {
            let result = observe::get_screenshot();
            serde_json::to_string(&result.unwrap())
                .unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "active_window" => {
            let result = observe::get_active_window();
            serde_json::to_string(&result.unwrap())
                .unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "user_activity_snapshot" => {
            let result = observe::get_user_activity_snapshot();
            serde_json::to_string(&result.unwrap())
                .unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "windows" => {
            let result = observe::list_windows();
            serde_json::to_string(&result.unwrap())
                .unwrap_or_else(|_| "{\"error\":\"json\"}".into())
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
            serde_json::to_string(&result.unwrap())
                .unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }

        // ── Overlay (Level 1) ──────────────────────────────
        "discord_status" => json_response(&discord_rpc::handle_status()),
        "discord_get_guilds" => {
            json_response(&discord_rpc::handle_json_command("get_guilds", params))
        }
        "discord_get_guild" => {
            json_response(&discord_rpc::handle_json_command("get_guild", params))
        }
        "discord_get_channels" => {
            json_response(&discord_rpc::handle_json_command("get_channels", params))
        }
        "discord_get_selected_voice_channel" => json_response(&discord_rpc::handle_json_command(
            "get_selected_voice_channel",
            params,
        )),
        "discord_get_voice_settings" => json_response(&discord_rpc::handle_json_command(
            "get_voice_settings",
            params,
        )),
        "discord_join_voice_channel" => json_response(&discord_rpc::handle_json_command(
            "join_voice_channel",
            params,
        )),
        "discord_join_voice_by_name" => json_response(&discord_rpc::handle_json_command(
            "join_voice_by_name",
            params,
        )),
        "discord_leave_voice_channel" => json_response(&discord_rpc::handle_json_command(
            "leave_voice_channel",
            params,
        )),
        "discord_select_text_channel" => json_response(&discord_rpc::handle_json_command(
            "select_text_channel",
            params,
        )),
        "discord_set_voice_settings" => json_response(&discord_rpc::handle_json_command(
            "set_voice_settings",
            params,
        )),
        "discord_set_activity" => {
            json_response(&discord_rpc::handle_json_command("set_activity", params))
        }
        "discord_unsupported_send_message" => json_response(&discord_rpc::handle_json_command(
            "unsupported_send_message",
            params,
        )),
        "show_overlay" => {
            let text = if params.is_empty() {
                "AEGIS Overlay"
            } else {
                params
            };
            OVERLAY_ACTIVE.store(true, std::sync::atomic::Ordering::Relaxed);
            *OVERLAY_TEXT.lock().unwrap() = text.to_string();
            json_response(&serde_json::json!({
                "status": "ok",
                "action": "show_overlay",
                "text": text,
            }))
        }
        "hide_overlay" => {
            OVERLAY_ACTIVE.store(false, std::sync::atomic::Ordering::Relaxed);
            *OVERLAY_TEXT.lock().unwrap() = String::new();
            "{\"status\":\"ok\",\"action\":\"hide_overlay\"}".to_string()
        }

        // ── App/Window (Level 1) ───────────────────────────
        "launch_app" => match system_ops::launch_app(params) {
            Ok(pid) => json_response(&serde_json::json!({
                "status": "ok",
                "action": "launch_app",
                "app": params,
                "pid": pid,
            })),
            Err(error) => json_error(error),
        },
        "focus_window" => match system_ops::focus_window(params) {
            Ok(()) => json_response(&serde_json::json!({
                "status": "ok",
                "action": "focus_window",
                "target": params,
            })),
            Err(error) => json_error(error),
        },

        // ── Input (Level 2: Approval required) ─────────────
        "mouse_move" => {
            let parts: Vec<&str> = params.split(',').collect();
            let x: i32 = parts
                .first()
                .and_then(|s| s.trim().parse().ok())
                .unwrap_or(0);
            let y: i32 = parts
                .get(1)
                .and_then(|s| s.trim().parse().ok())
                .unwrap_or(0);
            let result = action::mouse_move(x, y);
            serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "mouse_click" => {
            let parts: Vec<&str> = params.split(',').collect();
            let x: i32 = parts
                .first()
                .and_then(|s| s.trim().parse().ok())
                .unwrap_or(0);
            let y: i32 = parts
                .get(1)
                .and_then(|s| s.trim().parse().ok())
                .unwrap_or(0);
            let button = parts.get(2).map(|s| s.trim()).unwrap_or("left");
            if action::is_real_actions_enabled() {
                let result = action::mouse_click(x, y, button);
                serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            } else {
                "{\"status\":\"approval_required\",\"action\":\"mouse_click\",\"reason\":\"Mouse click requires user approval\"}".to_string()
            }
        }
        "keyboard_type" => {
            if action::is_real_actions_enabled() {
                let result = action::keyboard_type(params);
                serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            } else {
                "{\"status\":\"approval_required\",\"action\":\"keyboard_type\",\"reason\":\"Keyboard input requires user approval\"}".to_string()
            }
        }
        "press_hotkey" => {
            if action::is_real_actions_enabled() {
                let result = action::press_hotkey(params);
                serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            } else {
                "{\"status\":\"approval_required\",\"action\":\"press_hotkey\",\"reason\":\"Hotkey requires user approval\"}".to_string()
            }
        }

        // ── Observe Extended (Level 0) ──────────────────────
        "list_files" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let dir = parts.first().unwrap_or(&".");
            let recursive = parts.get(1).map(|s| s.trim() == "true").unwrap_or(false);
            match observe_ext::list_files(dir, recursive) {
                Ok(files) => {
                    serde_json::to_string(&files).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
                }
                Err(e) => json_error(e),
            }
        }
        "read_file" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let path = parts.first().unwrap_or(&"");
            let max_bytes: usize = parts
                .get(1)
                .and_then(|s| s.trim().parse().ok())
                .unwrap_or(10000);
            if crate::redaction::is_sensitive_directory(path)
                || crate::redaction::is_credential_file(path)
            {
                return "{\"status\":\"approval_required\",\"action\":\"read_file\",\"reason\":\"Sensitive file access requires approval\"}".to_string();
            }
            match observe_ext::read_file(path, max_bytes) {
                Ok(content) => json_response(&serde_json::json!({ "content": content })),
                Err(e) => json_error(e),
            }
        }
        "search_files" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let dir = parts.first().unwrap_or(&".");
            let pattern = parts.get(1).unwrap_or(&"");
            match observe_ext::search_files(dir, pattern) {
                Ok(files) => {
                    serde_json::to_string(&files).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
                }
                Err(e) => json_error(e),
            }
        }
        "list_processes" => match observe_ext::list_processes() {
            Ok(procs) => {
                serde_json::to_string(&procs).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "network_info" => match observe_ext::get_network_info() {
            Ok(info) => {
                serde_json::to_string(&info).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "disk_info" => match observe_ext::get_disk_info() {
            Ok(disks) => {
                serde_json::to_string(&disks).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "running_apps" => match observe_ext::list_running_apps() {
            Ok(apps) => {
                serde_json::to_string(&apps).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "env_vars" => match observe_ext::get_env_vars() {
            Ok(vars) => {
                serde_json::to_string(&vars).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "cwd" => match observe_ext::get_cwd() {
            Ok(dir) => json_response(&serde_json::json!({ "cwd": dir })),
            Err(e) => json_error(e),
        },

        // ── Overlay Approval (Level 2) ─────────────────────
        "overlay_approval" => {
            let request_id = format!(
                "req_{}",
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis()
            );
            let request = overlay_approval::ApprovalRequest {
                request_id: request_id.clone(),
                action: params.to_string(),
                description: format!("AEGIS requests approval for: {}", params),
                risk_level: "medium".to_string(),
                timeout_seconds: 30,
            };
            let result = overlay_approval::show_approval_overlay(request);
            serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }

        // ── Display Overlay (Level 0) ─────────────────────
        "show_display" => {
            let parts: Vec<&str> = params.splitn(3, '|').collect();
            let title = parts.first().unwrap_or(&"AEGIS").to_string();
            let body = parts.get(1).unwrap_or(&"").to_string();
            let duration: u32 = parts
                .get(2)
                .and_then(|s| s.trim().parse().ok())
                .unwrap_or(10);
            let request = overlay_approval::DisplayRequest {
                title,
                body,
                duration_seconds: duration,
                style: "info".to_string(),
            };
            let result = overlay_approval::show_display_overlay(request);
            serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }

        // ── Shell Execution (Level 2: Approval required) ──
        "show_rich_overlay" => {
            let mut request: overlay_approval::RichDisplayRequest =
                match serde_json::from_str(params.trim()) {
                    Ok(value) => value,
                    Err(e) => return json_error(format!("Invalid rich overlay JSON: {e}")),
                };
            if request.title.trim().is_empty() {
                request.title = "AEGIS".to_string();
            }
            if request.duration_seconds == 0 {
                request.duration_seconds = 8;
            }
            if request.style.trim().is_empty() {
                request.style = "info".to_string();
            }
            let result = overlay_approval::schedule_rich_display_overlay(request);
            serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "execute_shell" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let cmd = parts.first().unwrap_or(&"");
            let dir = parts.get(1).map(|s| s.trim()).filter(|s| !s.is_empty());
            let result = system_ops::execute_shell(cmd, dir);
            serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }
        "execute_powershell" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let cmd = parts.first().unwrap_or(&"");
            let dir = parts.get(1).map(|s| s.trim()).filter(|s| !s.is_empty());
            let result = system_ops::execute_powershell(cmd, dir);
            serde_json::to_string(&result).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }

        // ── File Operations (Level 2: Approval required) ──
        "write_file" => {
            let parts: Vec<&str> = params.splitn(3, '|').collect();
            let path = parts.first().unwrap_or(&"");
            let content = parts.get(1).unwrap_or(&"");
            let append = parts.get(2).map(|s| s.trim() == "true").unwrap_or(false);
            if crate::redaction::is_sensitive_directory(path)
                || crate::redaction::is_credential_file(path)
            {
                return "{\"status\":\"approval_required\",\"action\":\"write_file\",\"reason\":\"Sensitive file write requires approval\"}".to_string();
            }
            match system_ops::write_file(path, content, append) {
                Ok(_) => json_response(&serde_json::json!({
                    "status": "ok",
                    "action": "write_file",
                    "path": path,
                })),
                Err(e) => json_error(e),
            }
        }
        "delete_file" => {
            if safety::requires_approval("pc.delete_file") {
                return "{\"status\":\"approval_required\",\"action\":\"delete_file\",\"reason\":\"File deletion requires user approval\"}".to_string();
            }
            match system_ops::delete_file(params) {
                Ok(_) => "{\"status\":\"ok\",\"action\":\"delete_file\"}".to_string(),
                Err(e) => json_error(e),
            }
        }
        "copy_file" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let src = parts.first().unwrap_or(&"");
            let dst = parts.get(1).unwrap_or(&"");
            match system_ops::copy_file(src, dst) {
                Ok(bytes) => json_response(&serde_json::json!({
                    "status": "ok",
                    "action": "copy_file",
                    "bytes": bytes,
                })),
                Err(e) => json_error(e),
            }
        }
        "move_file" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let src = parts.first().unwrap_or(&"");
            let dst = parts.get(1).unwrap_or(&"");
            match system_ops::move_file(src, dst) {
                Ok(_) => "{\"status\":\"ok\",\"action\":\"move_file\"}".to_string(),
                Err(e) => json_error(e),
            }
        }
        "create_dir" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let path = parts.first().unwrap_or(&"");
            let recursive = parts.get(1).map(|s| s.trim() == "true").unwrap_or(true);
            match system_ops::create_dir(path, recursive) {
                Ok(_) => "{\"status\":\"ok\",\"action\":\"create_dir\"}".to_string(),
                Err(e) => json_error(e),
            }
        }
        "delete_dir" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let path = parts.first().unwrap_or(&"");
            let recursive = parts.get(1).map(|s| s.trim() == "true").unwrap_or(false);
            match system_ops::delete_dir(path, recursive) {
                Ok(_) => "{\"status\":\"ok\",\"action\":\"delete_dir\"}".to_string(),
                Err(e) => json_error(e),
            }
        }

        // ── Service Management (Level 2: Approval required) ──
        "list_services" => match system_ops::list_services() {
            Ok(services) => {
                serde_json::to_string(&services).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "start_service" => match system_ops::start_service(params) {
            Ok(_) => json_response(&serde_json::json!({
                "status": "ok",
                "action": "start_service",
                "service": params,
            })),
            Err(e) => json_error(e),
        },
        "stop_service" => match system_ops::stop_service(params) {
            Ok(_) => json_response(&serde_json::json!({
                "status": "ok",
                "action": "stop_service",
                "service": params,
            })),
            Err(e) => json_error(e),
        },

        // ── Scheduled Tasks ────────────────────────────────
        "list_scheduled_tasks" => match system_ops::list_scheduled_tasks() {
            Ok(tasks) => {
                serde_json::to_string(&tasks).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },

        // ── Registry ───────────────────────────────────────
        "read_registry" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let key = parts.first().unwrap_or(&"");
            let value = parts.get(1).unwrap_or(&"");
            match system_ops::read_registry(key, value) {
                Ok(val) => json_response(&serde_json::json!({ "value": val })),
                Err(e) => json_error(e),
            }
        }
        "list_registry_keys" => match system_ops::list_registry_keys(params) {
            Ok(keys) => {
                serde_json::to_string(&keys).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },

        // ── System Info ────────────────────────────────────
        "installed_software" => match system_ops::get_installed_software() {
            Ok(software) => {
                serde_json::to_string(&software).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "windows_features" => match system_ops::get_windows_features() {
            Ok(features) => {
                serde_json::to_string(&features).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "event_log" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let log_name = parts.first().unwrap_or(&"Application");
            let count: usize = parts
                .get(1)
                .and_then(|s| s.trim().parse().ok())
                .unwrap_or(10);
            match system_ops::get_event_log(log_name, count) {
                Ok(events) => {
                    serde_json::to_string(&events).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
                }
                Err(e) => json_error(e),
            }
        }
        "performance_counters" => match system_ops::get_performance_counters() {
            Ok(counters) => {
                serde_json::to_string(&counters).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },

        // ── Clipboard Operations ───────────────────────────
        "set_clipboard" => match system_ops::set_clipboard_text(params) {
            Ok(_) => "{\"status\":\"ok\",\"action\":\"set_clipboard\"}".to_string(),
            Err(e) => json_error(e),
        },
        "clipboard_image" => match system_ops::get_clipboard_image() {
            Ok(b64) => json_response(&serde_json::json!({ "image_base64": b64 })),
            Err(e) => json_error(e),
        },

        // ── System Actions ─────────────────────────────────
        "open_url" => match system_ops::open_url(params) {
            Ok(_) => json_response(&serde_json::json!({
                "status": "ok",
                "action": "open_url",
                "url": params,
            })),
            Err(e) => json_error(e),
        },
        "lock_workstation" => match system_ops::lock_workstation() {
            Ok(_) => "{\"status\":\"ok\",\"action\":\"lock_workstation\"}".to_string(),
            Err(e) => json_error(e),
        },
        "empty_recycle_bin" => match system_ops::empty_recycle_bin() {
            Ok(_) => "{\"status\":\"ok\",\"action\":\"empty_recycle_bin\"}".to_string(),
            Err(e) => json_error(e),
        },
        "file_metadata" => match system_ops::get_file_metadata(params) {
            Ok(meta) => {
                serde_json::to_string(&meta).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "set_file_permissions" => {
            let parts: Vec<&str> = params.splitn(2, '|').collect();
            let path = parts.first().unwrap_or(&"");
            let readonly = parts.get(1).map(|s| s.trim() == "true").unwrap_or(false);
            match system_ops::set_file_permissions(path, readonly) {
                Ok(_) => "{\"status\":\"ok\",\"action\":\"set_file_permissions\"}".to_string(),
                Err(e) => json_error(e),
            }
        }
        "get_env" => match system_ops::get_env_var(params) {
            Ok(val) => json_response(&serde_json::json!({ "name": params, "value": val })),
            Err(e) => json_error(e),
        },
        "logged_in_users" => match system_ops::get_logged_in_users() {
            Ok(users) => {
                serde_json::to_string(&users).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
            }
            Err(e) => json_error(e),
        },
        "capture_window" => match system_ops::capture_window(params) {
            Ok(b64) => json_response(&serde_json::json!({ "image_base64": b64 })),
            Err(e) => json_error(e),
        },

        // ── Capabilities ───────────────────────────────────
        "capabilities" => {
            let caps = safety::get_capabilities();
            serde_json::to_string(&caps).unwrap_or_else(|_| "{\"error\":\"json\"}".into())
        }

        // ── Control ────────────────────────────────────────
        "quit" => "{\"status\":\"ok\",\"action\":\"quit\"}".to_string(),

        _ => json_response(&serde_json::json!({
            "error": "unknown_command",
            "command": command,
        })),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::time::{SystemTime, UNIX_EPOCH};

    #[test]
    fn read_file_response_escapes_control_characters() {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!("aegis-read-file-json-{unique}.txt"));
        let content = "line1\r\nline2\t\"quoted\"\\slash\u{0008}";
        fs::write(&path, content).unwrap();

        let response = handle_command(&format!("read_file {}|10000", path.to_string_lossy()));
        let parsed: serde_json::Value = serde_json::from_str(&response).unwrap();

        assert_eq!(parsed["content"], content);
        fs::remove_file(path).unwrap();
    }

    #[test]
    fn json_error_escapes_windows_paths_and_controls() {
        let response = json_error("Failed at C:\\Users\\AEGIS\r\n\"quoted\"");
        let parsed: serde_json::Value = serde_json::from_str(&response).unwrap();

        assert_eq!(parsed["error"], "Failed at C:\\Users\\AEGIS\r\n\"quoted\"");
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
