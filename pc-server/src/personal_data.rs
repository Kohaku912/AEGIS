//! Personal Data Core collector: window/UIA/URL events + change-triggered JPEG.

use std::collections::{BTreeMap, HashSet, VecDeque};
use std::sync::{Mutex, OnceLock};
use std::thread;
use std::time::{Duration, Instant};

use base64::Engine;
use serde::Serialize;

use crate::observe;

const MAX_BUFFER: usize = 200;
const SAMPLE_MS: u64 = 500;
const SCREENSHOT_MIN_MS: u64 = 2000;

fn u32_is_zero(value: &u32) -> bool {
    *value == 0
}

#[derive(Debug, Clone, Serialize)]
pub struct PersonalDataEvent {
    pub timestamp_ms: u64,
    pub event_type: String,
    pub app_name: String,
    pub process_name: String,
    pub pid: u32,
    pub window_title: String,
    pub control_name: String,
    pub control_type: String,
    pub is_password: bool,
    pub value: String,
    pub url: String,
    pub scene_hash: String,
    #[serde(default, skip_serializing_if = "u32_is_zero")]
    pub keyboard_count: u32,
    #[serde(default, skip_serializing_if = "u32_is_zero")]
    pub mouse_count: u32,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub key_category_counts: BTreeMap<String, u32>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub keys: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub mouse_buttons: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub click_x: Option<i32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub click_y: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub screenshot_jpeg_base64: Option<String>,
}

#[derive(Default)]
struct Collector {
    buffer: VecDeque<PersonalDataEvent>,
    last_scene: String,
    last_window: String,
    last_control: String,
    last_value: String,
    last_windows: HashSet<String>,
    last_screenshot_at: Option<Instant>,
    windows_seeded: bool,
}

static COLLECTOR: OnceLock<Mutex<Collector>> = OnceLock::new();

fn collector() -> &'static Mutex<Collector> {
    COLLECTOR.get_or_init(|| Mutex::new(Collector::default()))
}

pub fn start_sampler() {
    thread::spawn(|| loop {
        sample_once();
        thread::sleep(Duration::from_millis(SAMPLE_MS));
    });
}

pub fn drain() -> Vec<PersonalDataEvent> {
    sample_once();
    let mut guard = collector().lock().unwrap_or_else(|e| e.into_inner());
    guard.buffer.drain(..).collect()
}

fn sample_once() {
    let snapshot = match observe::get_user_activity_snapshot() {
        Ok(value) => value,
        Err(_) => return,
    };
    let focus = capture_focus();
    let window_title = snapshot.active_window_title.clone();
    let mut control_name = focus.control_name.clone();
    let mut control_type = focus.control_type.clone();
    let mut is_password = focus.is_password;
    let value = focus.value.clone();
    let url = focus.url.clone();
    let scene_hash = format!(
        "{:x}",
        simple_hash(&format!(
            "{}|{}|{}|{}|{}",
            snapshot.process_name, window_title, control_name, url, value
        ))
    );

    let mouse_clicks = snapshot.mouse_count;
    let keyboard_count = snapshot.keyboard_count;
    let key_category_counts = nonzero_counts(&snapshot.key_category_counts);
    let keys = snapshot.keys.clone();
    let mouse_buttons = snapshot.mouse_buttons.clone();
    let click = if mouse_clicks > 0 {
        Some((snapshot.cursor_x, snapshot.cursor_y))
    } else {
        None
    };

    let mut pending: Vec<(String, String, String, bool)> = Vec::new();

    // Window open/close via list_windows key set.
    if let Ok(windows) = observe::list_windows() {
        let current: HashSet<String> = windows
            .iter()
            .filter(|w| w.is_visible && !w.title.trim().is_empty())
            .map(|w| format!("{}:{}:{}", w.pid, w.process_name, w.title))
            .collect();
        let mut guard = collector().lock().unwrap_or_else(|e| e.into_inner());
        if guard.windows_seeded {
            let opened: Vec<String> = current.difference(&guard.last_windows).cloned().collect();
            let closed: Vec<String> = guard.last_windows.difference(&current).cloned().collect();
            for key in opened {
                let parts: Vec<&str> = key.splitn(3, ':').collect();
                let title = parts.get(2).copied().unwrap_or("").to_string();
                let process = parts.get(1).copied().unwrap_or("").to_string();
                push_locked(
                    &mut guard,
                    PersonalDataEvent {
                        timestamp_ms: snapshot.timestamp_ms,
                        event_type: "pc.window.opened".into(),
                        app_name: process.clone(),
                        process_name: process,
                        pid: parts.first().and_then(|p| p.parse().ok()).unwrap_or(0),
                        window_title: title,
                        control_name: String::new(),
                        control_type: String::new(),
                        is_password: false,
                        value: String::new(),
                        url: String::new(),
                        scene_hash: scene_hash.clone(),
                        keyboard_count: 0,
                        mouse_count: 0,
                        key_category_counts: BTreeMap::new(),
                        keys: Vec::new(),
                        mouse_buttons: Vec::new(),
                        click_x: None,
                        click_y: None,
                        screenshot_jpeg_base64: None,
                    },
                );
            }
            for key in closed {
                let parts: Vec<&str> = key.splitn(3, ':').collect();
                let title = parts.get(2).copied().unwrap_or("").to_string();
                let process = parts.get(1).copied().unwrap_or("").to_string();
                push_locked(
                    &mut guard,
                    PersonalDataEvent {
                        timestamp_ms: snapshot.timestamp_ms,
                        event_type: "pc.window.closed".into(),
                        app_name: process.clone(),
                        process_name: process,
                        pid: parts.first().and_then(|p| p.parse().ok()).unwrap_or(0),
                        window_title: title,
                        control_name: String::new(),
                        control_type: String::new(),
                        is_password: false,
                        value: String::new(),
                        url: String::new(),
                        scene_hash: scene_hash.clone(),
                        keyboard_count: 0,
                        mouse_count: 0,
                        key_category_counts: BTreeMap::new(),
                        keys: Vec::new(),
                        mouse_buttons: Vec::new(),
                        click_x: None,
                        click_y: None,
                        screenshot_jpeg_base64: None,
                    },
                );
            }
        }
        guard.last_windows = current;
        guard.windows_seeded = true;
    }

    // Mouse activity → FromPoint invoke target.
    if mouse_clicks > 0 {
        if let Some(point) = capture_point() {
            control_name = point.control_name;
            control_type = point.control_type;
            is_password = point.is_password;
            pending.push((
                "pc.ui.invoked".into(),
                control_name.clone(),
                control_type.clone(),
                is_password,
            ));
        } else {
            pending.push((
                "pc.input.clicked".into(),
                control_name.clone(),
                control_type.clone(),
                is_password,
            ));
        }
    }

    if keyboard_count > 0 {
        pending.push((
            "pc.input.typed".into(),
            control_name.clone(),
            control_type.clone(),
            is_password,
        ));
    }

    {
        let guard = collector().lock().unwrap_or_else(|e| e.into_inner());
        if guard.last_window != window_title && !window_title.is_empty() {
            pending.push((
                "pc.window.focused".into(),
                control_name.clone(),
                control_type.clone(),
                is_password,
            ));
        } else if guard.last_control != control_name && !control_name.is_empty() && mouse_clicks == 0
        {
            pending.push((
                "pc.ui.focus_changed".into(),
                control_name.clone(),
                control_type.clone(),
                is_password,
            ));
        } else if !value.is_empty() && value != guard.last_value {
            pending.push((
                "pc.ui.value_changed".into(),
                control_name.clone(),
                control_type.clone(),
                is_password,
            ));
        } else if scene_hash == guard.last_scene && pending.is_empty() {
            return;
        }
    }

    if pending.is_empty() {
        pending.push((
            "pc.ui.focus_changed".into(),
            control_name.clone(),
            control_type.clone(),
            is_password,
        ));
    }

    let want_shot = {
        let guard = collector().lock().unwrap_or_else(|e| e.into_inner());
        let scene_changed = scene_hash != guard.last_scene;
        let cooled = guard
            .last_screenshot_at
            .map(|t| t.elapsed() >= Duration::from_millis(SCREENSHOT_MIN_MS))
            .unwrap_or(true);
        scene_changed && cooled
    };
    let screenshot = if want_shot {
        capture_jpeg().ok()
    } else {
        None
    };

    let mut guard = collector().lock().unwrap_or_else(|e| e.into_inner());
    for (idx, (event_type, cname, ctype, pass)) in pending.into_iter().enumerate() {
        let shot = if idx == 0 {
            screenshot.clone()
        } else {
            None
        };
        push_locked(
            &mut guard,
            PersonalDataEvent {
                timestamp_ms: snapshot.timestamp_ms,
                event_type,
                app_name: snapshot.app_name.clone(),
                process_name: snapshot.process_name.clone(),
                pid: snapshot.pid,
                window_title: window_title.clone(),
                control_name: cname,
                control_type: ctype,
                is_password: pass,
                value: value.clone(),
                url: url.clone(),
                scene_hash: scene_hash.clone(),
                keyboard_count,
                mouse_count: mouse_clicks,
                key_category_counts: key_category_counts.clone(),
                keys: keys.clone(),
                mouse_buttons: mouse_buttons.clone(),
                click_x: click.map(|pair| pair.0),
                click_y: click.map(|pair| pair.1),
                screenshot_jpeg_base64: shot,
            },
        );
    }
    if screenshot.is_some() {
        guard.last_screenshot_at = Some(Instant::now());
    }
    guard.last_scene = scene_hash;
    guard.last_window = window_title;
    guard.last_control = control_name;
    guard.last_value = value;
}

fn push_locked(guard: &mut Collector, event: PersonalDataEvent) {
    if guard.buffer.len() >= MAX_BUFFER {
        guard.buffer.pop_front();
    }
    guard.buffer.push_back(event);
}

struct FocusInfo {
    control_name: String,
    control_type: String,
    is_password: bool,
    value: String,
    url: String,
}

fn capture_focus() -> FocusInfo {
    #[cfg(target_os = "windows")]
    {
        let script = r#"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$el = [System.Windows.Automation.AutomationElement]::FocusedElement
if ($null -eq $el) { '{"control_name":"","control_type":"","is_password":false,"value":"","url":""}'; return }
$name = [string]$el.Current.Name
$ctype = [string]$el.Current.ControlType.ProgrammaticName
$pass = [bool]$el.Current.IsPassword
function Get-UiaValue($node) {
  if ($null -eq $node) { return '' }
  try {
    $vp = $node.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    if ($null -ne $vp) { $v = [string]$vp.Current.Value; if ($v) { return $v } }
  } catch {}
  try {
    $tp = $node.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
    if ($null -ne $tp) {
      $range = $tp.DocumentRange
      if ($null -ne $range) {
        $v = [string]$range.GetText(500)
        if ($v) { return $v }
      }
    }
  } catch {}
  try {
    $lp = $node.GetCurrentPattern([System.Windows.Automation.LegacyIAccessiblePattern]::Pattern)
    if ($null -ne $lp) {
      $v = [string]$lp.Current.Value
      if ($v) { return $v }
    }
  } catch {}
  return ''
}
$val = Get-UiaValue $el
$url = ''
$walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
$cur = $el
for ($i=0; $i -lt 12; $i++) {
  if ($null -eq $cur) { break }
  $n = [string]$cur.Current.Name
  $t = [string]$cur.Current.ControlType.ProgrammaticName
  if ($t -match 'Edit|Document' -and ($n -match 'Address|Search|URL|Omnibox|アドレス' -or $t -match 'Edit')) {
    $candidate = Get-UiaValue $cur
    if ($candidate -match '^https?://') { $url = $candidate; break }
    if (-not $url -and $candidate) { $url = $candidate }
  }
  $cur = $walker.GetParent($cur)
}
if (-not $url) {
  try {
    $proc = Get-Process -Id $el.Current.ProcessId -ErrorAction SilentlyContinue
    if ($null -ne $proc -and $proc.MainWindowHandle -ne 0) {
      $root = [System.Windows.Automation.AutomationElement]::FromHandle($proc.MainWindowHandle)
      if ($null -ne $root) {
        $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)
        foreach ($edit in $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond)) {
          $en = [string]$edit.Current.Name
          if ($en -match 'Address|Search|URL|Omnibox|アドレス') {
            $candidate = Get-UiaValue $edit
            if ($candidate) { $url = $candidate; break }
          }
        }
        if (-not $url) {
          $docCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Document)
          foreach ($doc in $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $docCond)) {
            $candidate = Get-UiaValue $doc
            if ($candidate -match '^https?://') { $url = $candidate; break }
          }
        }
      }
    }
  } catch {}
}
if ($val.Length -gt 500) { $val = $val.Substring(0,500) }
@{ control_name = $name; control_type = $ctype; is_password = $pass; value = $val; url = $url } | ConvertTo-Json -Compress
"#;
        if let Some(parsed) = run_ps_json(script) {
            return FocusInfo {
                control_name: parsed["control_name"].as_str().unwrap_or("").to_string(),
                control_type: parsed["control_type"].as_str().unwrap_or("").to_string(),
                is_password: parsed["is_password"].as_bool().unwrap_or(false),
                value: parsed["value"].as_str().unwrap_or("").to_string(),
                url: parsed["url"].as_str().unwrap_or("").to_string(),
            };
        }
    }
    FocusInfo {
        control_name: String::new(),
        control_type: String::new(),
        is_password: false,
        value: String::new(),
        url: String::new(),
    }
}

fn capture_point() -> Option<FocusInfo> {
    #[cfg(target_os = "windows")]
    {
        let script = r#"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName WindowsBase
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class AegisCursor {
  [StructLayout(LayoutKind.Sequential)]
  public struct POINT { public int X; public int Y; }
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT lpPoint);
}
"@
$pt = New-Object AegisCursor+POINT
[void][AegisCursor]::GetCursorPos([ref]$pt)
$el = [System.Windows.Automation.AutomationElement]::FromPoint((New-Object System.Windows.Point($pt.X, $pt.Y)))
if ($null -eq $el) { '{"control_name":"","control_type":"","is_password":false,"value":"","url":""}'; return }
$name = [string]$el.Current.Name
$ctype = [string]$el.Current.ControlType.ProgrammaticName
$pass = [bool]$el.Current.IsPassword
@{ control_name = $name; control_type = $ctype; is_password = $pass; value = ''; url = '' } | ConvertTo-Json -Compress
"#;
        if let Some(parsed) = run_ps_json(script) {
            return Some(FocusInfo {
                control_name: parsed["control_name"].as_str().unwrap_or("").to_string(),
                control_type: parsed["control_type"].as_str().unwrap_or("").to_string(),
                is_password: parsed["is_password"].as_bool().unwrap_or(false),
                value: String::new(),
                url: String::new(),
            });
        }
        None
    }
    #[cfg(not(target_os = "windows"))]
    {
        None
    }
}

fn run_ps_json(script: &str) -> Option<serde_json::Value> {
    let wrapped = format!(
        r#"[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false
$OutputEncoding = [Console]::OutputEncoding
$raw = & {{
{script}
}} | Out-String
$json = (($raw -split "`n") | Where-Object {{ $_.Trim().StartsWith('{{') }} | Select-Object -Last 1)
if (-not $json) {{ exit 1 }}
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($json.Trim()))
"#
    );
    let output = std::process::Command::new("powershell")
        .args(["-NoProfile", "-NonInteractive", "-Command", &wrapped])
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let encoded = decode_ps_stdout(&output.stdout);
    let bytes = base64::engine::general_purpose::STANDARD
        .decode(encoded.trim())
        .ok()?;
    serde_json::from_slice(&bytes).ok()
}

fn decode_ps_stdout(bytes: &[u8]) -> String {
    if let Ok(text) = std::str::from_utf8(bytes) {
        return text.to_string();
    }
    if bytes.len() >= 2 && bytes.len() % 2 == 0 {
        let units: Vec<u16> = bytes
            .chunks_exact(2)
            .map(|chunk| u16::from_le_bytes([chunk[0], chunk[1]]))
            .collect();
        return String::from_utf16_lossy(&units);
    }
    String::from_utf8_lossy(bytes).into_owned()
}

fn capture_jpeg() -> Result<String, String> {
    use image::{imageops, ImageBuffer, ImageFormat, Rgba};
    use screenshots::Screen;
    use std::io::Cursor;

    let screens = Screen::all().map_err(|e| e.to_string())?;
    let screen = screens.first().ok_or("no screen")?;
    let captured = screen.capture().map_err(|e| e.to_string())?;
    let width = captured.width();
    let height = captured.height();
    let mut img: ImageBuffer<Rgba<u8>, Vec<u8>> =
        ImageBuffer::from_raw(width, height, captured.rgba().to_vec()).ok_or("rgba")?;
    if width > 1280 {
        let new_h = (height as f32 * (1280.0 / width as f32)) as u32;
        img = imageops::resize(&img, 1280, new_h.max(1), imageops::FilterType::Triangle);
    }
    let mut out = Cursor::new(Vec::new());
    img.write_to(&mut out, ImageFormat::Jpeg)
        .map_err(|e| e.to_string())?;
    Ok(base64::engine::general_purpose::STANDARD.encode(out.into_inner()))
}

fn nonzero_counts(counts: &BTreeMap<String, u32>) -> BTreeMap<String, u32> {
    counts
        .iter()
        .filter(|(_, count)| **count > 0)
        .map(|(key, count)| (key.clone(), *count))
        .collect()
}

fn simple_hash(text: &str) -> u64 {
    let mut hash = 0xcbf29ce484222325u64;
    for byte in text.as_bytes() {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(0x100000001b3);
    }
    hash
}
