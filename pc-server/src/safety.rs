//! Capability safety definitions for PC Server.

use serde::{Deserialize, Serialize};

/// Safety level (matches AEGIS Core's SafetyLevel enum).
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[repr(u8)]
pub enum SafetyLevel {
    Level0Read = 1,
    Level1SafeAct = 2,
    Level2Approval = 3,
    Level3Restricted = 4,
}

/// Capability definition.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CapabilityDef {
    pub id: String,
    pub name: String,
    pub description: String,
    pub safety_level: SafetyLevel,
    pub requires_approval: bool,
    pub side_effects: Vec<String>,
    pub timeout_ms: u32,
    pub tags: Vec<String>,
}

/// Get all registered PC Server capabilities.
pub fn get_capabilities() -> Vec<CapabilityDef> {
    vec![
        // ── Observe (Level 0: Read-only) ──────────────────
        CapabilityDef {
            id: "pc.get_screenshot".into(),
            name: "Screenshot Capture".into(),
            description: "Capture the current display as a PNG image.".into(),
            safety_level: SafetyLevel::Level0Read,
            requires_approval: false,
            side_effects: vec![],
            timeout_ms: 5000,
            tags: vec!["screenshot".into(), "observe".into(), "read_only".into()],
        },
        CapabilityDef {
            id: "pc.get_active_window".into(),
            name: "Get Active Window".into(),
            description: "Return the title, process, and position of the foreground window.".into(),
            safety_level: SafetyLevel::Level0Read,
            requires_approval: false,
            side_effects: vec![],
            timeout_ms: 1000,
            tags: vec!["window".into(), "observe".into(), "read_only".into()],
        },
        CapabilityDef {
            id: "pc.list_windows".into(),
            name: "List Windows".into(),
            description: "List all visible windows with title and process info.".into(),
            safety_level: SafetyLevel::Level0Read,
            requires_approval: false,
            side_effects: vec![],
            timeout_ms: 2000,
            tags: vec!["window".into(), "observe".into(), "read_only".into()],
        },
        CapabilityDef {
            id: "pc.get_clipboard".into(),
            name: "Get Clipboard".into(),
            description: "Read the current clipboard text (secrets are redacted).".into(),
            safety_level: SafetyLevel::Level0Read,
            requires_approval: false,
            side_effects: vec![],
            timeout_ms: 500,
            tags: vec!["clipboard".into(), "observe".into(), "read_only".into()],
        },
        CapabilityDef {
            id: "pc.get_os_info".into(),
            name: "Get OS Info".into(),
            description: "Return OS name, version, hostname, username, and architecture.".into(),
            safety_level: SafetyLevel::Level0Read,
            requires_approval: false,
            side_effects: vec![],
            timeout_ms: 1000,
            tags: vec!["os".into(), "system".into(), "observe".into()],
        },
        CapabilityDef {
            id: "pc.get_screen_size".into(),
            name: "Get Screen Size".into(),
            description: "Return the screen resolution (width, height).".into(),
            safety_level: SafetyLevel::Level0Read,
            requires_approval: false,
            side_effects: vec![],
            timeout_ms: 500,
            tags: vec!["screen".into(), "observe".into(), "read_only".into()],
        },
        // ── Files (Level 0: Read-only, with restrictions) ──
        CapabilityDef {
            id: "pc.list_directory".into(),
            name: "List Directory".into(),
            description: "List files in a directory (sensitive dirs restricted).".into(),
            safety_level: SafetyLevel::Level0Read,
            requires_approval: false,
            side_effects: vec![],
            timeout_ms: 3000,
            tags: vec!["files".into(), "observe".into()],
        },
        // ── Overlay (Level 1: Safe action) ─────────────────
        CapabilityDef {
            id: "pc.show_overlay".into(),
            name: "Show Overlay".into(),
            description: "Display a text overlay on screen (e.g., memo, notification).".into(),
            safety_level: SafetyLevel::Level1SafeAct,
            requires_approval: false,
            side_effects: vec!["Displays UI overlay".into()],
            timeout_ms: 2000,
            tags: vec!["overlay".into(), "display".into()],
        },
        CapabilityDef {
            id: "pc.hide_overlay".into(),
            name: "Hide Overlay".into(),
            description: "Remove the current overlay from screen.".into(),
            safety_level: SafetyLevel::Level1SafeAct,
            requires_approval: false,
            side_effects: vec!["Removes UI overlay".into()],
            timeout_ms: 1000,
            tags: vec!["overlay".into(), "display".into()],
        },
        // ── Window Management (Level 1: Safe action) ───────
        CapabilityDef {
            id: "pc.launch_app".into(),
            name: "Launch Application".into(),
            description: "Launch an application by name or path.".into(),
            safety_level: SafetyLevel::Level1SafeAct,
            requires_approval: false,
            side_effects: vec!["Starts a process".into()],
            timeout_ms: 5000,
            tags: vec!["app".into(), "launch".into()],
        },
        CapabilityDef {
            id: "pc.focus_window".into(),
            name: "Focus Window".into(),
            description: "Bring a window to foreground by title or PID.".into(),
            safety_level: SafetyLevel::Level1SafeAct,
            requires_approval: false,
            side_effects: vec!["Changes window focus".into()],
            timeout_ms: 2000,
            tags: vec!["window".into(), "focus".into()],
        },
        // ── Input (Level 2: Approval required) ─────────────
        CapabilityDef {
            id: "pc.mouse_move".into(),
            name: "Mouse Move".into(),
            description: "Move mouse cursor to coordinates.".into(),
            safety_level: SafetyLevel::Level1SafeAct,
            requires_approval: false,
            side_effects: vec!["Moves mouse cursor".into()],
            timeout_ms: 1000,
            tags: vec!["mouse".into(), "input".into()],
        },
        CapabilityDef {
            id: "pc.mouse_click".into(),
            name: "Mouse Click".into(),
            description: "Click at screen coordinates. REQUIRES APPROVAL.".into(),
            safety_level: SafetyLevel::Level2Approval,
            requires_approval: true,
            side_effects: vec!["Clicks at coordinates".into()],
            timeout_ms: 3000,
            tags: vec!["mouse".into(), "input".into(), "approval_required".into()],
        },
        CapabilityDef {
            id: "pc.keyboard_type".into(),
            name: "Keyboard Type".into(),
            description: "Type text via keyboard. REQUIRES APPROVAL.".into(),
            safety_level: SafetyLevel::Level2Approval,
            requires_approval: true,
            side_effects: vec!["Inputs text".into()],
            timeout_ms: 5000,
            tags: vec!["keyboard".into(), "input".into(), "approval_required".into()],
        },
        CapabilityDef {
            id: "pc.press_hotkey".into(),
            name: "Press Hotkey".into(),
            description: "Press a keyboard shortcut. REQUIRES APPROVAL.".into(),
            safety_level: SafetyLevel::Level2Approval,
            requires_approval: true,
            side_effects: vec!["Triggers keyboard shortcut".into()],
            timeout_ms: 2000,
            tags: vec!["keyboard".into(), "hotkey".into(), "approval_required".into()],
        },
    ]
}

/// Check if a capability requires approval.
pub fn requires_approval(cap_id: &str) -> bool {
    get_capabilities()
        .iter()
        .find(|c| c.id == cap_id)
        .map(|c| c.requires_approval)
        .unwrap_or(true) // Default to requiring approval if unknown
}
