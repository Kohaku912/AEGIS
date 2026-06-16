//! Extended observe capabilities for PC Server.
//!
//! Additional read-only operations:
//! - File operations (read, list, search)
//! - Process listing
//! - Network information
//! - Disk information
//! - Running applications
//! - System notifications

use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Serialize, Deserialize)]
pub struct FileInfo {
    pub name: String,
    pub path: String,
    pub size_bytes: u64,
    pub is_dir: bool,
    pub modified_ms: u64,
    pub extension: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProcessInfo {
    pub pid: u32,
    pub name: String,
    pub cpu_usage: f32,
    pub memory_mb: u64,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct NetworkInfo {
    pub hostname: String,
    pub local_ip: String,
    pub interfaces: Vec<NetworkInterface>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct NetworkInterface {
    pub name: String,
    pub ip: String,
    pub mac: String,
    pub is_up: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DiskInfo {
    pub name: String,
    pub mount_point: String,
    pub total_bytes: u64,
    pub free_bytes: u64,
    pub used_bytes: u64,
    pub file_system: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RunningApp {
    pub name: String,
    pub pid: u32,
    pub window_title: String,
    pub exe_path: String,
}

/// List files in a directory
pub fn list_files(dir_path: &str, recursive: bool) -> Result<Vec<FileInfo>, String> {
    let path = Path::new(dir_path);
    if !path.exists() {
        return Err(format!("Directory not found: {}", dir_path));
    }
    if !path.is_dir() {
        return Err(format!("Not a directory: {}", dir_path));
    }

    let mut files = Vec::new();
    if recursive {
        collect_files_recursive(path, &mut files, 0, 3)?;
    } else {
        collect_files(path, &mut files)?;
    }
    Ok(files)
}

fn collect_files(dir: &Path, files: &mut Vec<FileInfo>) -> Result<(), String> {
    let entries = std::fs::read_dir(dir).map_err(|e| format!("Failed to read dir: {e}"))?;
    for entry in entries {
        let entry = entry.map_err(|e| format!("Failed to read entry: {e}"))?;
        let metadata = entry
            .metadata()
            .map_err(|e| format!("Failed to get metadata: {e}"))?;
        let name = entry.file_name().to_string_lossy().to_string();
        let path = entry.path().to_string_lossy().to_string();
        let extension = entry
            .path()
            .extension()
            .map(|e| e.to_string_lossy().to_string())
            .unwrap_or_default();

        files.push(FileInfo {
            name,
            path,
            size_bytes: metadata.len(),
            is_dir: metadata.is_dir(),
            modified_ms: metadata
                .modified()
                .map(|t| {
                    t.duration_since(std::time::UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_millis() as u64
                })
                .unwrap_or(0),
            extension,
        });
    }
    Ok(())
}

fn collect_files_recursive(
    dir: &Path,
    files: &mut Vec<FileInfo>,
    depth: usize,
    max_depth: usize,
) -> Result<(), String> {
    if depth >= max_depth {
        return Ok(());
    }
    let entries = std::fs::read_dir(dir).map_err(|e| format!("Failed to read dir: {e}"))?;
    for entry in entries {
        let entry = entry.map_err(|e| format!("Failed to read entry: {e}"))?;
        let metadata = entry
            .metadata()
            .map_err(|e| format!("Failed to get metadata: {e}"))?;
        let name = entry.file_name().to_string_lossy().to_string();
        let path = entry.path().to_string_lossy().to_string();
        let extension = entry
            .path()
            .extension()
            .map(|e| e.to_string_lossy().to_string())
            .unwrap_or_default();

        files.push(FileInfo {
            name,
            path: path.clone(),
            size_bytes: metadata.len(),
            is_dir: metadata.is_dir(),
            modified_ms: metadata
                .modified()
                .map(|t| {
                    t.duration_since(std::time::UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_millis() as u64
                })
                .unwrap_or(0),
            extension,
        });

        if metadata.is_dir() {
            collect_files_recursive(&entry.path(), files, depth + 1, max_depth)?;
        }
    }
    Ok(())
}

/// Read file content as text
pub fn read_file(file_path: &str, max_bytes: usize) -> Result<String, String> {
    let path = Path::new(file_path);
    if !path.exists() {
        return Err(format!("File not found: {}", file_path));
    }
    if !path.is_file() {
        return Err(format!("Not a file: {}", file_path));
    }

    let content = std::fs::read(path).map_err(|e| format!("Failed to read file: {e}"))?;
    let content = if content.len() > max_bytes {
        &content[..max_bytes]
    } else {
        &content
    };

    String::from_utf8(content.to_vec()).map_err(|_| "File is not valid UTF-8".to_string())
}

/// Search for files matching a pattern
pub fn search_files(dir_path: &str, pattern: &str) -> Result<Vec<FileInfo>, String> {
    let files = list_files(dir_path, true)?;
    let pattern_lower = pattern.to_lowercase();
    Ok(files
        .into_iter()
        .filter(|f| f.name.to_lowercase().contains(&pattern_lower))
        .collect())
}

/// List running processes
pub fn list_processes() -> Result<Vec<ProcessInfo>, String> {
    use sysinfo::System;
    let mut system = System::new_all();
    system.refresh_all();

    Ok(system
        .processes()
        .values()
        .map(|p| ProcessInfo {
            pid: p.pid().as_u32(),
            name: p.name().to_string(),
            cpu_usage: p.cpu_usage(),
            memory_mb: p.memory() / 1024 / 1024,
            status: format!("{:?}", p.status()),
        })
        .collect())
}

/// Get network information
pub fn get_network_info() -> Result<NetworkInfo, String> {
    let hostname = hostname::get()
        .map(|h| h.to_string_lossy().to_string())
        .unwrap_or_else(|_| "unknown".to_string());

    Ok(NetworkInfo {
        hostname,
        local_ip: local_ip_address::local_ip()
            .map(|ip| ip.to_string())
            .unwrap_or_else(|_| "0.0.0.0".to_string()),
        interfaces: Vec::new(),
    })
}

/// Get disk information
pub fn get_disk_info() -> Result<Vec<DiskInfo>, String> {
    use sysinfo::Disks;
    let disks = Disks::new_with_refreshed_list();

    Ok(disks
        .iter()
        .map(|d| DiskInfo {
            name: d.name().to_string_lossy().to_string(),
            mount_point: d.mount_point().to_string_lossy().to_string(),
            total_bytes: d.total_space(),
            free_bytes: d.available_space(),
            used_bytes: d.total_space() - d.available_space(),
            file_system: d.file_system().to_string_lossy().to_string(),
        })
        .collect())
}

/// List running applications with windows
pub fn list_running_apps() -> Result<Vec<RunningApp>, String> {
    let windows = x_win::get_open_windows().map_err(|e| format!("Failed to list windows: {e}"))?;
    Ok(windows
        .into_iter()
        .map(|w| RunningApp {
            name: w.info.exec_name,
            pid: w.info.process_id,
            window_title: w.title,
            exe_path: String::new(),
        })
        .collect())
}

/// Get environment variables
pub fn get_env_vars() -> Result<std::collections::HashMap<String, String>, String> {
    Ok(std::env::vars().collect())
}

/// Get current working directory
pub fn get_cwd() -> Result<String, String> {
    std::env::current_dir()
        .map(|p| p.to_string_lossy().to_string())
        .map_err(|e| format!("Failed to get cwd: {e}"))
}
