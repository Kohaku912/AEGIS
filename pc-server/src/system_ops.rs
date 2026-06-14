//! Shell and system management capabilities.
//!
//! Additional operations:
//! - Shell command execution
//! - PowerShell execution
//! - File write/delete/copy/move
//! - Registry operations
//! - Service management
//! - Task scheduler
//! - Windows features

use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
pub struct ShellResult {
    pub success: bool,
    pub stdout: String,
    pub stderr: String,
    pub exit_code: i32,
    pub duration_ms: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ServiceInfo {
    pub name: String,
    pub display_name: String,
    pub status: String,
    pub start_type: String,
    pub pid: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TaskInfo {
    pub name: String,
    pub status: String,
    pub next_run: String,
    pub last_run: String,
    pub author: String,
}

/// Execute a shell command
pub fn execute_shell(command: &str, working_dir: Option<&str>) -> ShellResult {
    let start = std::time::Instant::now();
    
    let mut cmd = if cfg!(target_os = "windows") {
        let mut c = Command::new("cmd");
        c.args(&["/C", command]);
        c
    } else {
        let mut c = Command::new("sh");
        c.args(&["-c", command]);
        c
    };

    if let Some(dir) = working_dir {
        cmd.current_dir(dir);
    }

    let output = cmd.output();
    let duration = start.elapsed().as_millis() as u64;

    match output {
        Ok(output) => ShellResult {
            success: output.status.success(),
            stdout: String::from_utf8_lossy(&output.stdout).to_string(),
            stderr: String::from_utf8_lossy(&output.stderr).to_string(),
            exit_code: output.status.code().unwrap_or(-1),
            duration_ms: duration,
        },
        Err(e) => ShellResult {
            success: false,
            stdout: String::new(),
            stderr: format!("Failed to execute: {}", e),
            exit_code: -1,
            duration_ms: duration,
        },
    }
}

/// Execute a PowerShell command
pub fn execute_powershell(command: &str, working_dir: Option<&str>) -> ShellResult {
    let start = std::time::Instant::now();
    
    let mut cmd = Command::new("powershell");
    cmd.args(&["-NoProfile", "-NonInteractive", "-Command", command]);

    if let Some(dir) = working_dir {
        cmd.current_dir(dir);
    }

    let output = cmd.output();
    let duration = start.elapsed().as_millis() as u64;

    match output {
        Ok(output) => ShellResult {
            success: output.status.success(),
            stdout: String::from_utf8_lossy(&output.stdout).to_string(),
            stderr: String::from_utf8_lossy(&output.stderr).to_string(),
            exit_code: output.status.code().unwrap_or(-1),
            duration_ms: duration,
        },
        Err(e) => ShellResult {
            success: false,
            stdout: String::new(),
            stderr: format!("Failed to execute: {}", e),
            exit_code: -1,
            duration_ms: duration,
        },
    }
}

/// Write content to a file
pub fn write_file(path: &str, content: &str, append: bool) -> Result<(), String> {
    use std::fs::OpenOptions;
    use std::io::Write;

    let mut options = OpenOptions::new();
    if append {
        options.append(true);
    } else {
        options.write(true).truncate(true);
    }
    options.create(true);

    let mut file = options.open(path).map_err(|e| format!("Failed to open file: {e}"))?;
    file.write_all(content.as_bytes()).map_err(|e| format!("Failed to write: {e}"))?;
    Ok(())
}

/// Delete a file
pub fn delete_file(path: &str) -> Result<(), String> {
    std::fs::remove_file(path).map_err(|e| format!("Failed to delete: {e}"))
}

/// Copy a file
pub fn copy_file(src: &str, dst: &str) -> Result<u64, String> {
    std::fs::copy(src, dst).map_err(|e| format!("Failed to copy: {e}"))
}

/// Move/rename a file
pub fn move_file(src: &str, dst: &str) -> Result<(), String> {
    std::fs::rename(src, dst).map_err(|e| format!("Failed to move: {e}"))
}

/// Create a directory
pub fn create_dir(path: &str, recursive: bool) -> Result<(), String> {
    if recursive {
        std::fs::create_dir_all(path).map_err(|e| format!("Failed to create dir: {e}"))
    } else {
        std::fs::create_dir(path).map_err(|e| format!("Failed to create dir: {e}"))
    }
}

/// Delete a directory
pub fn delete_dir(path: &str, recursive: bool) -> Result<(), String> {
    if recursive {
        std::fs::remove_dir_all(path).map_err(|e| format!("Failed to delete dir: {e}"))
    } else {
        std::fs::remove_dir(path).map_err(|e| format!("Failed to delete dir: {e}"))
    }
}

/// List Windows services
pub fn list_services() -> Result<Vec<ServiceInfo>, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            "Get-Service | Select-Object Name, DisplayName, Status, StartType | ConvertTo-Json"])
        .output()
        .map_err(|e| format!("Failed to list services: {e}"))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let services: Vec<serde_json::Value> = serde_json::from_str(&stdout)
        .unwrap_or_default();

    Ok(services.into_iter().map(|s| ServiceInfo {
        name: s["Name"].as_str().unwrap_or("").to_string(),
        display_name: s["DisplayName"].as_str().unwrap_or("").to_string(),
        status: s["Status"].as_str().unwrap_or("").to_string(),
        start_type: s["StartType"].as_str().unwrap_or("").to_string(),
        pid: 0,
    }).collect())
}

/// Start a Windows service
pub fn start_service(name: &str) -> Result<(), String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            &format!("Start-Service -Name '{}'", name)])
        .output()
        .map_err(|e| format!("Failed to start service: {e}"))?;

    if output.status.success() {
        Ok(())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// Stop a Windows service
pub fn stop_service(name: &str) -> Result<(), String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            &format!("Stop-Service -Name '{}' -Force", name)])
        .output()
        .map_err(|e| format!("Failed to stop service: {e}"))?;

    if output.status.success() {
        Ok(())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// List scheduled tasks
pub fn list_scheduled_tasks() -> Result<Vec<TaskInfo>, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            "Get-ScheduledTask | Select-Object TaskName, State, @{N='NextRun';E={$_.Triggers[0].StartBoundary}}, @{N='LastRun';E={$_.Info.LastRunTime}}, Author | ConvertTo-Json"])
        .output()
        .map_err(|e| format!("Failed to list tasks: {e}"))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let tasks: Vec<serde_json::Value> = serde_json::from_str(&stdout)
        .unwrap_or_default();

    Ok(tasks.into_iter().map(|t| TaskInfo {
        name: t["TaskName"].as_str().unwrap_or("").to_string(),
        status: t["State"].as_str().unwrap_or("").to_string(),
        next_run: t["NextRun"].as_str().unwrap_or("").to_string(),
        last_run: t["LastRun"].as_str().unwrap_or("").to_string(),
        author: t["Author"].as_str().unwrap_or("").to_string(),
    }).collect())
}

/// Read a registry value
pub fn read_registry(key: &str, value_name: &str) -> Result<String, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            &format!("(Get-ItemProperty -Path '{}' -Name '{}').'{}'", key, value_name, value_name)])
        .output()
        .map_err(|e| format!("Failed to read registry: {e}"))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// List registry keys
pub fn list_registry_keys(key: &str) -> Result<Vec<String>, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            &format!("Get-ChildItem -Path '{}' | Select-Object -ExpandProperty Name", key)])
        .output()
        .map_err(|e| format!("Failed to list registry: {e}"))?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.lines().map(|s| s.to_string()).collect())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// Get installed software
pub fn get_installed_software() -> Result<Vec<String>, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName | ConvertTo-Json"])
        .output()
        .map_err(|e| format!("Failed to get software: {e}"))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let software: Vec<serde_json::Value> = serde_json::from_str(&stdout)
        .unwrap_or_default();

    Ok(software.into_iter()
        .filter_map(|s| s["DisplayName"].as_str().map(|s| s.to_string()))
        .collect())
}

/// Get Windows features
pub fn get_windows_features() -> Result<Vec<String>, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            "Get-WindowsOptionalFeature -Online | Where-Object {$_.State -eq 'Enabled'} | Select-Object FeatureName | ConvertTo-Json"])
        .output()
        .map_err(|e| format!("Failed to get features: {e}"))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let features: Vec<serde_json::Value> = serde_json::from_str(&stdout)
        .unwrap_or_default();

    Ok(features.into_iter()
        .filter_map(|f| f["FeatureName"].as_str().map(|s| s.to_string()))
        .collect())
}

/// Get event log entries
pub fn get_event_log(log_name: &str, count: usize) -> Result<Vec<String>, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            &format!("Get-EventLog -LogName '{}' -Newest {} | Select-Object TimeGenerated, EntryType, Message | ConvertTo-Json", log_name, count)])
        .output()
        .map_err(|e| format!("Failed to get event log: {e}"))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let events: Vec<serde_json::Value> = serde_json::from_str(&stdout)
        .unwrap_or_default();

    Ok(events.into_iter()
        .map(|e| format!("{} [{}] {}",
            e["TimeGenerated"].as_str().unwrap_or(""),
            e["EntryType"].as_str().unwrap_or(""),
            e["Message"].as_str().unwrap_or("").chars().take(100).collect::<String>()))
        .collect())
}

/// Get performance counters
pub fn get_performance_counters() -> Result<serde_json::Value, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            r#"@{
    CPU = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
    Memory = (Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue
    Disk = (Get-Counter '\PhysicalDisk(_Total)\% Disk Time').CounterSamples.CookedValue
} | ConvertTo-Json"#])
        .output()
        .map_err(|e| format!("Failed to get counters: {e}"))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    serde_json::from_str(&stdout).map_err(|e| format!("Failed to parse: {e}"))
}

/// Take a screenshot of a specific window
pub fn capture_window(title: &str) -> Result<String, String> {
    // Use PowerShell to capture specific window
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            &format!(r#"
Add-Type -AssemblyName System.Windows.Forms
$proc = Get-Process | Where-Object {{$_.MainWindowTitle -like '*{}*'}} | Select-Object -First 1
if ($proc) {{
    $hwnd = $proc.MainWindowHandle
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {{
        [DllImport("user32.dll")]
        public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
        [DllImport("user32.dll")]
        public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    }}
    public struct RECT {{
        public int Left, Top, Right, Bottom;
    }}
"@
    $rect = New-Object RECT
    [Win32]::GetWindowRect($hwnd, [ref]$rect)
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    $bmp = New-Object System.Drawing.Bitmap($width, $height)
    $gfx = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $gfx.GetHdc()
    [Win32]::PrintWindow($hwnd, $hdc, 0)
    $gfx.ReleaseHdc($hdc)
    $path = "$env:TEMP\aegis_window_capture.png"
    $bmp.Save($path)
    $gfx.Dispose()
    $bmp.Dispose()
    Write-Output $path
}} else {{
    Write-Error "Window not found"
}}
"#, title)])
        .output()
        .map_err(|e| format!("Failed to capture window: {e}"))?;

    if output.status.success() {
        let path = String::from_utf8_lossy(&output.stdout).trim().to_string();
        // Read and encode the image
        let image_data = std::fs::read(&path).map_err(|e| format!("Failed to read image: {e}"))?;
        Ok(base64::Engine::encode(&base64::engine::general_purpose::STANDARD, &image_data))
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// Open a URL in the default browser
pub fn open_url(url: &str) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        Command::new("cmd")
            .args(&["/C", "start", url])
            .output()
            .map_err(|e| format!("Failed to open URL: {e}"))?;
        Ok(())
    }
    #[cfg(not(target_os = "windows"))]
    {
        Command::new("xdg-open")
            .arg(url)
            .output()
            .map_err(|e| format!("Failed to open URL: {e}"))?;
        Ok(())
    }
}

/// Get clipboard image as base64
pub fn get_clipboard_image() -> Result<String, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            r#"
Add-Type -AssemblyName System.Windows.Forms
$clip = [System.Windows.Forms.Clipboard]::GetImage()
if ($clip) {
    $path = "$env:TEMP\aegis_clipboard.png"
    $clip.Save($path)
    [Convert]::ToBase64String([IO.File]::ReadAllBytes($path))
} else {
    Write-Error "No image in clipboard"
}
"#])
        .output()
        .map_err(|e| format!("Failed to get clipboard image: {e}"))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// Set clipboard text
pub fn set_clipboard_text(text: &str) -> Result<(), String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            &format!("Set-Clipboard -Value '{}'", text.replace('\'', "''"))])
        .output()
        .map_err(|e| format!("Failed to set clipboard: {e}"))?;

    if output.status.success() {
        Ok(())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// Get file metadata
pub fn get_file_metadata(path: &str) -> Result<serde_json::Value, String> {
    let metadata = std::fs::metadata(path).map_err(|e| format!("Failed to get metadata: {e}"))?;
    
    Ok(serde_json::json!({
        "size_bytes": metadata.len(),
        "is_dir": metadata.is_dir(),
        "is_file": metadata.is_file(),
        "readonly": metadata.permissions().readonly(),
        "modified": metadata.modified()
            .map(|t| t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs())
            .unwrap_or(0),
        "created": metadata.created()
            .map(|t| t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs())
            .unwrap_or(0),
        "accessed": metadata.accessed()
            .map(|t| t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs())
            .unwrap_or(0),
    }))
}

/// Change file permissions
pub fn set_file_permissions(path: &str, readonly: bool) -> Result<(), String> {
    let mut perms = std::fs::metadata(path)
        .map_err(|e| format!("Failed to get metadata: {e}"))?
        .permissions();
    perms.set_readonly(readonly);
    std::fs::set_permissions(path, perms)
        .map_err(|e| format!("Failed to set permissions: {e}"))
}

/// Get environment variable
pub fn get_env_var(name: &str) -> Result<String, String> {
    std::env::var(name).map_err(|e| format!("Failed to get env var: {e}"))
}

/// Set environment variable (for current process)
pub fn set_env_var(name: &str, value: &str) {
    std::env::set_var(name, value);
}

/// Get system uptime
pub fn get_system_uptime() -> Result<u64, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"])
        .output()
        .map_err(|e| format!("Failed to get uptime: {e}"))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    // Parse and calculate uptime
    Ok(0) // Simplified
}

/// Get logged in users
pub fn get_logged_in_users() -> Result<Vec<String>, String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            "query user 2>$null | Select-Object -Skip 1 | ForEach-Object { ($_ -split '\\s+')[1] }"])
        .output()
        .map_err(|e| format!("Failed to get users: {e}"))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    Ok(stdout.lines().filter(|s| !s.is_empty()).map(|s| s.to_string()).collect())
}

/// Lock the workstation
pub fn lock_workstation() -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        let output = Command::new("powershell")
            .args(&["-NoProfile", "-NonInteractive", "-Command", "rundll32.exe user32.dll,LockWorkStation"])
            .output()
            .map_err(|e| format!("Failed to lock: {e}"))?;
        if output.status.success() {
            Ok(())
        } else {
            Err("Failed to lock workstation".to_string())
        }
    }
    #[cfg(not(target_os = "windows"))]
    {
        Err("Not supported on this platform".to_string())
    }
}

/// Empty the recycle bin
pub fn empty_recycle_bin() -> Result<(), String> {
    let output = Command::new("powershell")
        .args(&["-NoProfile", "-NonInteractive", "-Command",
            "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"])
        .output()
        .map_err(|e| format!("Failed to empty recycle bin: {e}"))?;

    if output.status.success() {
        Ok(())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}
