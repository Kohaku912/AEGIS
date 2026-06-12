//! Health endpoint for PC Server.
//!
//! Simple TCP JSON health check that AI Server and Docker can use.
//! Protocol: Send "health\n" → receive JSON health status.

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

static START_TIME: std::sync::OnceLock<std::time::Instant> = std::sync::OnceLock::new();

fn get_uptime() -> u64 {
    START_TIME.get_or_init(std::time::Instant::now).elapsed().as_secs()
}

fn handle_client(mut stream: TcpStream) {
    let reader = BufReader::new(stream.try_clone().unwrap());
    for line in reader.lines() {
        match line {
            Ok(cmd) if cmd.trim() == "health" => {
                let os_info = observe::get_os_info();
                let status = HealthStatus {
                    status: "ok".to_string(),
                    server_id: "pc-server-host".to_string(),
                    version: "0.1.0".to_string(),
                    capabilities: safety::get_capabilities().len(),
                    os_name: os_info.os_name,
                    os_version: os_info.os_version,
                    uptime_seconds: get_uptime(),
                };
                let json = serde_json::to_string(&status).unwrap();
                let _ = stream.write_all(format!("{}\n", json).as_bytes());
                let _ = stream.flush();
            }
            Ok(cmd) if cmd.trim() == "screenshot" => {
                let result = observe::get_screenshot();
                let json = serde_json::to_string(&result.unwrap()).unwrap();
                let _ = stream.write_all(format!("{}\n", json).as_bytes());
                let _ = stream.flush();
            }
            Ok(cmd) if cmd.trim() == "active_window" => {
                let result = observe::get_active_window();
                let json = serde_json::to_string(&result.unwrap()).unwrap();
                let _ = stream.write_all(format!("{}\n", json).as_bytes());
                let _ = stream.flush();
            }
            Ok(cmd) if cmd.trim() == "windows" => {
                let result = observe::list_windows();
                let json = serde_json::to_string(&result.unwrap()).unwrap();
                let _ = stream.write_all(format!("{}\n", json).as_bytes());
                let _ = stream.flush();
            }
            Ok(cmd) if cmd.trim() == "os_info" => {
                let result = observe::get_os_info();
                let json = serde_json::to_string(&result).unwrap();
                let _ = stream.write_all(format!("{}\n", json).as_bytes());
                let _ = stream.flush();
            }
            Ok(cmd) if cmd.trim() == "quit" => {
                break;
            }
            Err(_) => break,
            _ => {
                let _ = stream.write_all(b"ERR unknown command\n");
            }
        }
    }
}

/// Start the health server on the given address.
pub fn start_health_server(addr: &str) {
    let listener = TcpListener::bind(addr).expect("Failed to bind health server");
    println!("PC Server health endpoint listening on {}", addr);

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
