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
        // ── Actions (skeletons — not implemented) ─────────
        CapabilityDef {
            id: "pc.mouse_click".into(),
            name: "Mouse Click (SKELETON)".into(),
            description: "Click at screen coordinates. NOT YET IMPLEMENTED.".into(),
            safety_level: SafetyLevel::Level1SafeAct,
            requires_approval: false,
            side_effects: vec!["Modifies UI state".into()],
            timeout_ms: 3000,
            tags: vec!["mouse".into(), "input".into(), "skeleton".into()],
        },
        CapabilityDef {
            id: "pc.keyboard_type".into(),
            name: "Keyboard Type (SKELETON)".into(),
            description: "Type text via keyboard. NOT YET IMPLEMENTED.".into(),
            safety_level: SafetyLevel::Level1SafeAct,
            requires_approval: false,
            side_effects: vec!["Inputs text".into()],
            timeout_ms: 5000,
            tags: vec!["keyboard".into(), "input".into(), "skeleton".into()],
        },
    ]
}
