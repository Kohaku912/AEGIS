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
//! - file listing/reading/searching
//! - process listing
//! - network info
//! - disk info
//! - running apps
//! - environment variables
//! - current directory
//!
//! Action capabilities (Level 1):
//! - overlay display
//! - app launch
//! - window focus
//! - mouse move
//! - window resize/minimize/maximize/close
//! - mouse drag/scroll
//!
//! Elevated (Level 2, annotated — not gated):
//! - mouse click
//! - keyboard type
//! - press hotkey
//! - file write/delete
//! - process kill
//! - overlay confirmation (Y/N key)

mod action;
mod discord_rpc;
mod health;
mod observe;
mod observe_ext;
mod overlay_approval;
mod personal_data;
mod redaction;
mod safety;
mod system_ops;
mod uia;

use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.contains(&"--help".to_string()) {
        print_help();
        return;
    }

    let port = args
        .windows(2)
        .find(|w| w[0] == "--port")
        .map(|w| w[1].clone())
        .unwrap_or_else(|| "50052".to_string());

    let bind_addr = args
        .windows(2)
        .find(|w| w[0] == "--bind")
        .map(|w| w[1].clone())
        .unwrap_or_else(|| "127.0.0.1".to_string());

    let enable_real_actions = args.contains(&"--enable-real-pc-actions".to_string());

    let full_addr = format!("{}:{}", bind_addr, port);

    println!("AEGIS PC Server v0.2.0");
    println!("========================");
    println!();

    let caps = safety::get_capabilities();
    let observe_count = caps
        .iter()
        .filter(|c| c.safety_level == safety::SafetyLevel::Level0Read)
        .count();
    let action_count = caps
        .iter()
        .filter(|c| c.safety_level == safety::SafetyLevel::Level1SafeAct)
        .count();
    let elevated_count = caps
        .iter()
        .filter(|c| c.safety_level == safety::SafetyLevel::Level2Approval)
        .count();

    println!("Capabilities: {} total", caps.len());
    println!("  Observe (Level 0): {}", observe_count);
    println!("  Action (Level 1):  {}", action_count);
    println!("  Elevated (Level 2): {}", elevated_count);
    println!();

    let info = observe::get_os_info();
    println!(
        "OS: {} {} ({})",
        info.os_name, info.os_version, info.architecture
    );
    println!("Host: {} / {}", info.hostname, info.username);

    let screen = observe::get_screen_size();
    println!("Screen: {}x{}", screen.width, screen.height);

    println!();
    println!("Bind: {}", full_addr);
    println!(
        "Real PC actions: {}",
        if enable_real_actions {
            "ENABLED"
        } else {
            "DISABLED (mock)"
        }
    );
    println!();
    println!(
        "Commands: health, screenshot, active_window, windows, os_info, screen_size, clipboard"
    );
    println!("          show_overlay, show_rich_overlay, launch_app, close_window");
    println!("          mouse_move, mouse_click, keyboard_type, press_hotkey (runtime-enabled)");
    println!("          discord_status, discord_get_guilds, discord_join_voice_by_name");
    println!("          capabilities, quit");
    println!();
    println!("PC Server ready.");
    println!("Press Ctrl+C to stop.");
    println!();

    crate::personal_data::start_sampler();
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
    println!("  --bind <ADDR>              Bind address (default: 127.0.0.1)");
    println!("  --enable-real-pc-actions   Enable real mouse/keyboard actions");
    println!("  --help                     Show this help");
    println!();
    println!("Observe capabilities (Level 0):");
    println!("  pc-server.screenshot.get_screenshot  Capture screen as PNG");
    println!("  pc-server.window.get_active_window   Get foreground window info");
    println!("  pc-server.window.list_windows        List all visible windows");
    println!("  pc-server.clipboard.get_clipboard    Read clipboard (redacted)");
    println!("  pc-server.system.get_os_info         Get OS information");
    println!("  pc-server.system.get_screen_size     Get screen resolution");
    println!();
    println!("Action capabilities (Level 1):");
    println!("  pc-server.system.show_overlay        Display text overlay");
    println!("  pc-server.overlay.show_rich          Display rich overlay");
    println!("  pc-server.system.launch_app          Launch application");
    println!("  pc-server.window.close_window        Close a window");
    println!("  pc-server.input.mouse_move           Move mouse cursor");
    println!();
    println!("Elevated (Level 2 — a descriptive tier, nobody is asked):");
    println!("  pc-server.input.mouse_click          Click at coordinates");
    println!("  pc-server.input.keyboard_type        Type text");
    println!("  pc-server.input.press_hotkey         Press keyboard shortcut");
    println!("  pc-server.discord.status             Check Discord RPC readiness");
    println!("  pc-server.discord.join_voice_by_name Join Discord voice by server/channel name");
    println!();
    println!("The authoritative inventory is the 58 manifests under");
    println!("ai-server/capabilities/builtin/pc-server/. The ids above are a summary.");
}
