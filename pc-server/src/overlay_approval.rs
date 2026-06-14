//! Overlay Approval UI — keyboard-based approval.
//!
//! Shows approval request and captures Y/N key input.
//! Blocks until user responds or timeout.

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ApprovalRequest {
    pub request_id: String,
    pub action: String,
    pub description: String,
    pub risk_level: String,
    pub timeout_seconds: u32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ApprovalResult {
    pub approved: bool,
    pub request_id: String,
    pub response: String,
}

/// Show approval prompt and wait for Y/N response
pub fn show_approval_overlay(request: ApprovalRequest) -> ApprovalResult {
    #[cfg(target_os = "windows")]
    {
        use std::io::{self, Write};
        
        println!("\n========================================");
        println!("AEGIS Approval Required");
        println!("========================================");
        println!("Action: {}", request.action);
        println!("Description: {}", request.description);
        println!("Risk Level: {}", request.risk_level);
        println!("Timeout: {} seconds", request.timeout_seconds);
        println!("========================================");
        println!("Press Y to Approve, N to Reject, ESC to Cancel");
        println!("========================================");
        io::stdout().flush().unwrap_or_default();

        let start = std::time::Instant::now();
        let timeout = std::time::Duration::from_secs(request.timeout_seconds as u64);

        loop {
            if start.elapsed() > timeout {
                return ApprovalResult {
                    approved: false,
                    request_id: request.request_id,
                    response: "Timeout".to_string(),
                };
            }

            unsafe {
                use windows_sys::Win32::UI::Input::KeyboardAndMouse::*;
                
                if GetAsyncKeyState(0x59) & 0x8000u16 as i16 != 0 {
                    println!("\nApproved!");
                    return ApprovalResult {
                        approved: true,
                        request_id: request.request_id,
                        response: "Approved with Y key".to_string(),
                    };
                }
                
                if GetAsyncKeyState(0x4E) & 0x8000u16 as i16 != 0 {
                    println!("\nRejected!");
                    return ApprovalResult {
                        approved: false,
                        request_id: request.request_id,
                        response: "Rejected with N key".to_string(),
                    };
                }
                
                if GetAsyncKeyState(VK_ESCAPE as i32) & 0x8000u16 as i16 != 0 {
                    println!("\nCancelled!");
                    return ApprovalResult {
                        approved: false,
                        request_id: request.request_id,
                        response: "Cancelled with Escape".to_string(),
                    };
                }
            }

            std::thread::sleep(std::time::Duration::from_millis(100));
        }
    }

    #[cfg(not(target_os = "windows"))]
    {
        ApprovalResult {
            approved: false,
            request_id: request.request_id,
            response: "Overlay only supported on Windows".to_string(),
        }
    }
}
