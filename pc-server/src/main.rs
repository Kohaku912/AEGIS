//! AEGIS PC Server — OS-native PC observation and automation
//!
//! Observe capabilities:
//! - health check (TCP JSON)
//! - screenshot capture (mock)
//! - active window detection (mock)
//! - window listing (mock)
//! - clipboard read with secret redaction (mock)
//! - OS info
//!
//! Action capabilities (skeleton only — not yet implemented):
//! - mouse/keyboard input
//! - app launch
//! - file operations

mod health;
mod observe;
mod redaction;
mod safety;

use std::env;
use std::thread;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.contains(&"--help".to_string()) {
        println!("AEGIS PC Server v0.1.0");
        println!();
        println!("Usage: aegis-pc-server [OPTIONS]");
        println!();
        println!("Options:");
        println!("  --port <PORT>        Health endpoint port (default: 50052)");
        println!("  --bind <ADDR>        Bind address (default: 0.0.0.0)");
        println!("  --enable-real-pc-actions  Enable real mouse/keyboard (requires approval)");
        println!("  --help               Show this help");
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

    println!("AEGIS PC Server v0.1.0");
    println!("Capabilities loaded: {}", safety::get_capabilities().len());

    let info = observe::get_os_info();
    println!("OS: {} {} ({})", info.os_name, info.os_version, info.architecture);

    let win = observe::get_active_window().unwrap();
    println!("Active window: {} (pid={})", win.title, win.pid);

    println!("Bind: {}", full_addr);
    println!("Real PC actions: {}", if enable_real_actions { "ENABLED" } else { "DISABLED (mock)" });
    println!();
    println!("PC Server ready.");
    println!("Health endpoint: {}:{}", bind_addr, port);
    println!("Press Ctrl+C to stop.");
    println!();

    // Start health server
    health::start_health_server(&full_addr);
}
