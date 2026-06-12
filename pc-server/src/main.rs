//! AEGIS PC Server — OS-native PC observation and automation
//!
//! Observe capabilities (Level 0):
//! - health check (TCP JSON)
//! - screenshot capture
//! - active window detection
//! - window listing
//! - clipboard read with secret redaction
//! - OS info
//! - screen size
//!
//! Action capabilities (Level 1):
//! - overlay display
//! - app launch
//! - window focus
//! - mouse move
//!
//! Approval-required (Level 2):
//! - mouse click
//! - keyboard type
//! - press hotkey

mod action;
mod health;
mod observe;
mod redaction;
mod safety;

use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.contains(&"--help".to_string()) {
        print_help();
        return;
    }

    let port = args.windows(2)
        .find(|w| w[0] == "--port")
        .map(|w| w[1].clone())
        .unwrap_or_else(|| "50052".to_string());

    let bind_addr = args.windows(2)
        .find(|w| w[0] == "--bind")
        .map(|w| w[1].clone())
        .unwrap_or_else(|| "0.0.0.0".to_string());

    let enable_real_actions = args.contains(&"--enable-real-pc-actions".to_string());

    let full_addr = format!("{}:{}", bind_addr, port);

    println!("AEGIS PC Server v0.2.0");
    println!("========================");
    println!();

    let caps = safety::get_capabilities();
    let observe_count = caps.iter().filter(|c| c.safety_level == safety::SafetyLevel::Level0Read).count();
    let action_count = caps.iter().filter(|c| c.safety_level == safety::SafetyLevel::Level1SafeAct).count();
    let approval_count = caps.iter().filter(|c| c.safety_level == safety::SafetyLevel::Level2Approval).count();

    println!("Capabilities: {} total", caps.len());
    println!("  Observe (Level 0): {}", observe_count);
    println!("  Action (Level 1):  {}", action_count);
    println!("  Approval (Level 2): {}", approval_count);
    println!();

    let info = observe::get_os_info();
    println!("OS: {} {} ({})", info.os_name, info.os_version, info.architecture);
    println!("Host: {} / {}", info.hostname, info.username);

    let screen = observe::get_screen_size();
    println!("Screen: {}x{}", screen.width, screen.height);

    println!();
    println!("Bind: {}", full_addr);
    println!("Real PC actions: {}", if enable_real_actions { "ENABLED" } else { "DISABLED (mock)" });
    println!();
    println!("Commands: health, screenshot, active_window, windows, os_info, screen_size, clipboard");
    println!("          show_overlay, hide_overlay, launch_app, focus_window");
    println!("          mouse_move, mouse_click, keyboard_type, press_hotkey (approval required)");
    println!("          capabilities, quit");
    println!();
    println!("PC Server ready.");
    println!("Press Ctrl+C to stop.");
    println!();

    // Start health server
    health::start_health_server(&full_addr);
}

fn print_help() {
    println!("AEGIS PC Server v0.2.0");
    println!();
    println!("Usage: aegis-pc-server [OPTIONS]");
    println!();
    println!("Options:");
    println!("  --port <PORT>              Health endpoint port (default: 50052)");
    println!("  --bind <ADDR>              Bind address (default: 0.0.0.0)");
    println!("  --enable-real-pc-actions   Enable real mouse/keyboard (requires approval)");
    println!("  --help                     Show this help");
    println!();
    println!("Observe capabilities (Level 0):");
    println!("  pc.get_screenshot     Capture screen as PNG");
    println!("  pc.get_active_window  Get foreground window info");
    println!("  pc.list_windows       List all visible windows");
    println!("  pc.get_clipboard      Read clipboard (redacted)");
    println!("  pc.get_os_info        Get OS information");
    println!("  pc.get_screen_size    Get screen resolution");
    println!();
    println!("Action capabilities (Level 1):");
    println!("  pc.show_overlay       Display text overlay");
    println!("  pc.hide_overlay       Remove overlay");
    println!("  pc.launch_app         Launch application");
    println!("  pc.focus_window       Bring window to front");
    println!("  pc.mouse_move         Move mouse cursor");
    println!();
    println!("Approval-required (Level 2):");
    println!("  pc.mouse_click        Click at coordinates");
    println!("  pc.keyboard_type      Type text");
    println!("  pc.press_hotkey       Press keyboard shortcut");
}
