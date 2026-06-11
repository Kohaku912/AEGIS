//! AEGIS PC Server — OS-native PC observation and automation
//!
//! Observe capabilities (Phase 4.1):
//! - health check
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

mod observe;
mod redaction;
mod safety;
mod server;

fn main() {
    println!("AEGIS PC Server v0.1.0");
    println!("Capabilities loaded: {}", safety::get_capabilities().len());

    let info = observe::get_os_info();
    println!("OS: {} {} ({})", info.os_name, info.os_version, info.architecture);

    let win = observe::get_active_window().unwrap();
    println!("Active window: {} (pid={})", win.title, win.pid);

    println!("PC Server ready (mock mode).");
    println!("Press Ctrl+C to stop.");

    loop {
        std::thread::sleep(std::time::Duration::from_secs(10));
    }
}
