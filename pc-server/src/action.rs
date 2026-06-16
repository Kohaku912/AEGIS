//! Windows-native action capabilities.
//!
//! Uses Windows API (SendInput) for mouse/keyboard control.
//! All actions require the --enable-real-pc-actions flag.

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct ActionResult {
    pub success: bool,
    pub action: String,
    pub details: String,
}

/// Check if real PC actions are enabled.
pub fn is_real_actions_enabled() -> bool {
    std::env::args().any(|a| a == "--enable-real-pc-actions")
}

/// Move mouse to coordinates.
pub fn mouse_move(x: i32, y: i32) -> ActionResult {
    if !is_real_actions_enabled() {
        return ActionResult {
            success: true,
            action: "mouse_move".into(),
            details: format!("[MOCK] Moved mouse to ({}, {})", x, y),
        };
    }

    #[cfg(target_os = "windows")]
    {
        unsafe {
            use windows_sys::Win32::UI::Input::KeyboardAndMouse::*;

            let input = INPUT {
                r#type: INPUT_MOUSE,
                Anonymous: INPUT_0 {
                    mi: MOUSEINPUT {
                        dx: x,
                        dy: y,
                        mouseData: 0,
                        dwFlags: MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                        time: 0,
                        dwExtraInfo: 0,
                    },
                },
            };
            SendInput(1, &input, std::mem::size_of::<INPUT>() as i32);
        }
        ActionResult {
            success: true,
            action: "mouse_move".into(),
            details: format!("Moved mouse to ({}, {})", x, y),
        }
    }

    #[cfg(not(target_os = "windows"))]
    ActionResult {
        success: false,
        action: "mouse_move".into(),
        details: "Only supported on Windows".into(),
    }
}

/// Click at coordinates.
pub fn mouse_click(x: i32, y: i32, button: &str) -> ActionResult {
    if !is_real_actions_enabled() {
        return ActionResult {
            success: true,
            action: "mouse_click".into(),
            details: format!("[MOCK] Clicked {} at ({}, {})", button, x, y),
        };
    }

    #[cfg(target_os = "windows")]
    {
        unsafe {
            use windows_sys::Win32::UI::Input::KeyboardAndMouse::*;

            // Move to position
            let move_input = INPUT {
                r#type: INPUT_MOUSE,
                Anonymous: INPUT_0 {
                    mi: MOUSEINPUT {
                        dx: x,
                        dy: y,
                        mouseData: 0,
                        dwFlags: MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                        time: 0,
                        dwExtraInfo: 0,
                    },
                },
            };
            SendInput(1, &move_input, std::mem::size_of::<INPUT>() as i32);

            // Click
            let (down_flag, up_flag) = match button {
                "right" => (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
                "middle" => (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
                _ => (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
            };

            let down = INPUT {
                r#type: INPUT_MOUSE,
                Anonymous: INPUT_0 {
                    mi: MOUSEINPUT {
                        dx: 0,
                        dy: 0,
                        mouseData: 0,
                        dwFlags: down_flag,
                        time: 0,
                        dwExtraInfo: 0,
                    },
                },
            };
            SendInput(1, &down, std::mem::size_of::<INPUT>() as i32);

            let up = INPUT {
                r#type: INPUT_MOUSE,
                Anonymous: INPUT_0 {
                    mi: MOUSEINPUT {
                        dx: 0,
                        dy: 0,
                        mouseData: 0,
                        dwFlags: up_flag,
                        time: 0,
                        dwExtraInfo: 0,
                    },
                },
            };
            SendInput(1, &up, std::mem::size_of::<INPUT>() as i32);
        }
        ActionResult {
            success: true,
            action: "mouse_click".into(),
            details: format!("Clicked {} at ({}, {})", button, x, y),
        }
    }

    #[cfg(not(target_os = "windows"))]
    ActionResult {
        success: false,
        action: "mouse_click".into(),
        details: "Only supported on Windows".into(),
    }
}

/// Type text via keyboard.
pub fn keyboard_type(text: &str) -> ActionResult {
    if !is_real_actions_enabled() {
        return ActionResult {
            success: true,
            action: "keyboard_type".into(),
            details: format!("[MOCK] Typed {} chars", text.len()),
        };
    }

    #[cfg(target_os = "windows")]
    {
        unsafe {
            use windows_sys::Win32::UI::Input::KeyboardAndMouse::*;

            for ch in text.chars() {
                let mut inputs = [
                    INPUT {
                        r#type: INPUT_KEYBOARD,
                        Anonymous: INPUT_0 {
                            ki: KEYBDINPUT {
                                wVk: 0,
                                wScan: ch as u16,
                                dwFlags: KEYEVENTF_UNICODE,
                                time: 0,
                                dwExtraInfo: 0,
                            },
                        },
                    },
                    INPUT {
                        r#type: INPUT_KEYBOARD,
                        Anonymous: INPUT_0 {
                            ki: KEYBDINPUT {
                                wVk: 0,
                                wScan: ch as u16,
                                dwFlags: KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                                time: 0,
                                dwExtraInfo: 0,
                            },
                        },
                    },
                ];
                SendInput(2, inputs.as_mut_ptr(), std::mem::size_of::<INPUT>() as i32);
            }
        }
        ActionResult {
            success: true,
            action: "keyboard_type".into(),
            details: format!("Typed {} chars", text.len()),
        }
    }

    #[cfg(not(target_os = "windows"))]
    ActionResult {
        success: false,
        action: "keyboard_type".into(),
        details: "Only supported on Windows".into(),
    }
}

/// Press a hotkey combination.
pub fn press_hotkey(keys: &str) -> ActionResult {
    if !is_real_actions_enabled() {
        return ActionResult {
            success: true,
            action: "press_hotkey".into(),
            details: format!("[MOCK] Pressed hotkey: {}", keys),
        };
    }

    // Parse keys like "ctrl+c", "alt+tab", "ctrl+shift+s"
    let key_parts: Vec<&str> = keys.split('+').map(|k| k.trim()).collect();
    let mut vk_codes: Vec<u16> = Vec::new();

    for key in &key_parts {
        let vk = match key.to_lowercase().as_str() {
            "ctrl" | "control" => 0x11,
            "alt" => 0x12,
            "shift" => 0x10,
            "win" | "meta" => 0x5B,
            "tab" => 0x09,
            "enter" | "return" => 0x0D,
            "escape" | "esc" => 0x1B,
            "space" => 0x20,
            "backspace" => 0x08,
            "delete" | "del" => 0x2E,
            "a" => 0x41,
            "b" => 0x42,
            "c" => 0x43,
            "d" => 0x44,
            "e" => 0x45,
            "f" => 0x46,
            "g" => 0x47,
            "h" => 0x48,
            "i" => 0x49,
            "j" => 0x4A,
            "k" => 0x4B,
            "l" => 0x4C,
            "m" => 0x4D,
            "n" => 0x4E,
            "o" => 0x4F,
            "p" => 0x50,
            "q" => 0x51,
            "r" => 0x52,
            "s" => 0x53,
            "t" => 0x54,
            "u" => 0x55,
            "v" => 0x56,
            "w" => 0x57,
            "x" => 0x58,
            "y" => 0x59,
            "z" => 0x5A,
            "1" => 0x31,
            "2" => 0x32,
            "3" => 0x33,
            "4" => 0x34,
            "5" => 0x35,
            "6" => 0x36,
            "7" => 0x37,
            "8" => 0x38,
            "9" => 0x39,
            "0" => 0x30,
            _ => 0,
        };
        if vk != 0 {
            vk_codes.push(vk);
        }
    }

    #[cfg(target_os = "windows")]
    {
        unsafe {
            use windows_sys::Win32::UI::Input::KeyboardAndMouse::*;

            // Press all keys down
            for &vk in &vk_codes {
                let input = INPUT {
                    r#type: INPUT_KEYBOARD,
                    Anonymous: INPUT_0 {
                        ki: KEYBDINPUT {
                            wVk: vk,
                            wScan: 0,
                            dwFlags: 0,
                            time: 0,
                            dwExtraInfo: 0,
                        },
                    },
                };
                SendInput(1, &input, std::mem::size_of::<INPUT>() as i32);
            }

            // Release all keys in reverse order
            for &vk in vk_codes.iter().rev() {
                let input = INPUT {
                    r#type: INPUT_KEYBOARD,
                    Anonymous: INPUT_0 {
                        ki: KEYBDINPUT {
                            wVk: vk,
                            wScan: 0,
                            dwFlags: KEYEVENTF_KEYUP,
                            time: 0,
                            dwExtraInfo: 0,
                        },
                    },
                };
                SendInput(1, &input, std::mem::size_of::<INPUT>() as i32);
            }
        }
        ActionResult {
            success: true,
            action: "press_hotkey".into(),
            details: format!("Pressed hotkey: {}", keys),
        }
    }

    #[cfg(not(target_os = "windows"))]
    ActionResult {
        success: false,
        action: "press_hotkey".into(),
        details: "Only supported on Windows".into(),
    }
}
