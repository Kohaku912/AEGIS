//! Overlay — click-through overlay with keyboard input.
//!
//! Approval overlay: Y = approve, N = reject, ESC = cancel.
//! Display overlay: Shows arbitrary text, auto-dismisses or ESC to close.

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

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DisplayRequest {
    pub title: String,
    pub body: String,
    pub duration_seconds: u32,
    pub style: String,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct RichDisplayRequest {
    pub title: String,
    pub body: String,
    pub duration_seconds: u32,
    pub style: String,
    pub image_base64: Option<String>,
    pub image_mime: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DisplayResult {
    pub shown: bool,
    pub response: String,
}

#[cfg(target_os = "windows")]
struct OverlayData {
    action: String,
    description: String,
    risk_level: String,
}

#[cfg(target_os = "windows")]
static mut OVERLAY_DATA: Option<OverlayData> = None;

pub fn show_approval_overlay(request: ApprovalRequest) -> ApprovalResult {
    #[cfg(target_os = "windows")]
    {
        use windows_sys::Win32::UI::Input::KeyboardAndMouse::*;
        use windows_sys::Win32::UI::WindowsAndMessaging::*;

        unsafe {
            OVERLAY_DATA = Some(OverlayData {
                action: request.action.clone(),
                description: request.description.clone(),
                risk_level: request.risk_level.clone(),
            });

            let h_instance =
                windows_sys::Win32::System::LibraryLoader::GetModuleHandleW(std::ptr::null());

            let class_name: Vec<u16> = "AegisApprovalOverlay\0".encode_utf16().collect();

            let wc = WNDCLASSEXW {
                cbSize: std::mem::size_of::<WNDCLASSEXW>() as u32,
                style: CS_HREDRAW | CS_VREDRAW,
                lpfnWndProc: Some(overlay_wnd_proc),
                cbClsExtra: 0,
                cbWndExtra: 0,
                hInstance: h_instance,
                hbrBackground: std::ptr::null_mut(),
                lpszMenuName: std::ptr::null(),
                lpszClassName: class_name.as_ptr(),
                hCursor: std::ptr::null_mut(),
                hIcon: std::ptr::null_mut(),
                hIconSm: std::ptr::null_mut(),
            };

            RegisterClassExW(&wc);

            let screen_w = GetSystemMetrics(SM_CXSCREEN);
            let wnd_w = 480;
            let wnd_h = 200;
            let x = (screen_w - wnd_w) / 2;
            let y = 40;

            let title: Vec<u16> = "AEGIS\0".encode_utf16().collect();

            let hwnd = CreateWindowExW(
                WS_EX_TOPMOST | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW,
                class_name.as_ptr(),
                title.as_ptr(),
                WS_POPUP | WS_VISIBLE,
                x,
                y,
                wnd_w,
                wnd_h,
                std::ptr::null_mut(),
                std::ptr::null_mut(),
                h_instance,
                std::ptr::null(),
            );

            if hwnd.is_null() {
                OVERLAY_DATA = None;
                return ApprovalResult {
                    approved: false,
                    request_id: request.request_id,
                    response: "Failed to create overlay".to_string(),
                };
            }

            SetLayeredWindowAttributes(hwnd, 0, 230, LWA_ALPHA);

            ShowWindow(hwnd, SW_SHOWNOACTIVATE);

            let start = std::time::Instant::now();
            let timeout = std::time::Duration::from_secs(request.timeout_seconds as u64);

            loop {
                if start.elapsed() > timeout {
                    DestroyWindow(hwnd);
                    OVERLAY_DATA = None;
                    return ApprovalResult {
                        approved: false,
                        request_id: request.request_id,
                        response: "Timeout".to_string(),
                    };
                }

                let mut msg: MSG = std::mem::zeroed();
                while PeekMessageW(&mut msg, hwnd, 0, 0, PM_REMOVE) != 0 {
                    if msg.message == WM_PAINT {
                        TranslateMessage(&msg);
                        DispatchMessageW(&msg);
                    }
                }

                if GetAsyncKeyState(VK_Y as i32) as u16 & 0x8000 != 0 {
                    std::thread::sleep(std::time::Duration::from_millis(100));
                    DestroyWindow(hwnd);
                    OVERLAY_DATA = None;
                    return ApprovalResult {
                        approved: true,
                        request_id: request.request_id,
                        response: "Approved with Y key".to_string(),
                    };
                }

                if GetAsyncKeyState(VK_N as i32) as u16 & 0x8000 != 0 {
                    std::thread::sleep(std::time::Duration::from_millis(100));
                    DestroyWindow(hwnd);
                    OVERLAY_DATA = None;
                    return ApprovalResult {
                        approved: false,
                        request_id: request.request_id,
                        response: "Rejected with N key".to_string(),
                    };
                }

                if GetAsyncKeyState(VK_ESCAPE as i32) as u16 & 0x8000 != 0 {
                    std::thread::sleep(std::time::Duration::from_millis(100));
                    DestroyWindow(hwnd);
                    OVERLAY_DATA = None;
                    return ApprovalResult {
                        approved: false,
                        request_id: request.request_id,
                        response: "Cancelled with ESC".to_string(),
                    };
                }

                std::thread::sleep(std::time::Duration::from_millis(50));
            }
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

#[cfg(target_os = "windows")]
static mut DISPLAY_DATA: Option<DisplayData> = None;

#[cfg(target_os = "windows")]
struct DisplayData {
    title: String,
    body: String,
    style: String,
}

#[cfg(target_os = "windows")]
static mut RICH_DISPLAY_DATA: Option<RichDisplayData> = None;

#[cfg(target_os = "windows")]
struct RichDisplayData {
    title: String,
    body: String,
    style: String,
    image_bgra: Option<Vec<u8>>,
    image_width: i32,
    image_height: i32,
}

pub fn show_display_overlay(request: DisplayRequest) -> DisplayResult {
    #[cfg(target_os = "windows")]
    {
        use windows_sys::Win32::UI::Input::KeyboardAndMouse::*;
        use windows_sys::Win32::UI::WindowsAndMessaging::*;

        unsafe {
            DISPLAY_DATA = Some(DisplayData {
                title: request.title.clone(),
                body: request.body.clone(),
                style: request.style.clone(),
            });

            let h_instance =
                windows_sys::Win32::System::LibraryLoader::GetModuleHandleW(std::ptr::null());

            let class_name: Vec<u16> = "AegisDisplayOverlay\0".encode_utf16().collect();

            let wc = WNDCLASSEXW {
                cbSize: std::mem::size_of::<WNDCLASSEXW>() as u32,
                style: CS_HREDRAW | CS_VREDRAW,
                lpfnWndProc: Some(display_wnd_proc),
                cbClsExtra: 0,
                cbWndExtra: 0,
                hInstance: h_instance,
                hbrBackground: std::ptr::null_mut(),
                lpszMenuName: std::ptr::null(),
                lpszClassName: class_name.as_ptr(),
                hCursor: std::ptr::null_mut(),
                hIcon: std::ptr::null_mut(),
                hIconSm: std::ptr::null_mut(),
            };

            RegisterClassExW(&wc);

            let screen_w = GetSystemMetrics(SM_CXSCREEN);

            let body_lines = request.body.lines().count().max(1);
            let wnd_h = std::cmp::min(600, 80 + body_lines as i32 * 24 + 40);
            let wnd_w = 500;
            let x = (screen_w - wnd_w) / 2;
            let y = 40;

            let title: Vec<u16> = "AEGIS\0".encode_utf16().collect();

            let hwnd = CreateWindowExW(
                WS_EX_TOPMOST | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW,
                class_name.as_ptr(),
                title.as_ptr(),
                WS_POPUP | WS_VISIBLE,
                x,
                y,
                wnd_w,
                wnd_h,
                std::ptr::null_mut(),
                std::ptr::null_mut(),
                h_instance,
                std::ptr::null(),
            );

            if hwnd.is_null() {
                DISPLAY_DATA = None;
                return DisplayResult {
                    shown: false,
                    response: "Failed to create overlay".to_string(),
                };
            }

            SetLayeredWindowAttributes(hwnd, 0, 220, LWA_ALPHA);

            ShowWindow(hwnd, SW_SHOWNOACTIVATE);

            let start = std::time::Instant::now();
            let duration = if request.duration_seconds == 0 {
                10
            } else {
                request.duration_seconds
            };
            let timeout = std::time::Duration::from_secs(duration as u64);

            loop {
                if start.elapsed() > timeout {
                    DestroyWindow(hwnd);
                    DISPLAY_DATA = None;
                    return DisplayResult {
                        shown: true,
                        response: "Displayed".to_string(),
                    };
                }

                let mut msg: MSG = std::mem::zeroed();
                while PeekMessageW(&mut msg, hwnd, 0, 0, PM_REMOVE) != 0 {
                    if msg.message == WM_PAINT {
                        TranslateMessage(&msg);
                        DispatchMessageW(&msg);
                    }
                }

                if GetAsyncKeyState(VK_ESCAPE as i32) as u16 & 0x8000 != 0 {
                    std::thread::sleep(std::time::Duration::from_millis(100));
                    DestroyWindow(hwnd);
                    DISPLAY_DATA = None;
                    return DisplayResult {
                        shown: true,
                        response: "Dismissed with ESC".to_string(),
                    };
                }

                std::thread::sleep(std::time::Duration::from_millis(50));
            }
        }
    }

    #[cfg(not(target_os = "windows"))]
    {
        DisplayResult {
            shown: false,
            response: "Overlay only supported on Windows".to_string(),
        }
    }
}

pub fn show_rich_display_overlay(request: RichDisplayRequest) -> DisplayResult {
    #[cfg(target_os = "windows")]
    {
        use base64::Engine;
        use windows_sys::Win32::UI::Input::KeyboardAndMouse::*;
        use windows_sys::Win32::UI::WindowsAndMessaging::*;

        let mut image_bgra = None;
        let mut image_width = 0;
        let mut image_height = 0;
        if let Some(encoded) = request
            .image_base64
            .as_deref()
            .filter(|s| !s.trim().is_empty())
        {
            match base64::engine::general_purpose::STANDARD.decode(encoded) {
                Ok(bytes) => match image::load_from_memory(&bytes) {
                    Ok(img) => {
                        let rgba = img.to_rgba8();
                        image_width = rgba.width() as i32;
                        image_height = rgba.height() as i32;
                        let mut bgra = Vec::with_capacity(rgba.len());
                        for px in rgba.chunks_exact(4) {
                            bgra.extend_from_slice(&[px[2], px[1], px[0], px[3]]);
                        }
                        image_bgra = Some(bgra);
                    }
                    Err(e) => {
                        return DisplayResult {
                            shown: false,
                            response: format!("Failed to decode image: {e}"),
                        };
                    }
                },
                Err(e) => {
                    return DisplayResult {
                        shown: false,
                        response: format!("Invalid image_base64: {e}"),
                    };
                }
            }
        }

        unsafe {
            RICH_DISPLAY_DATA = Some(RichDisplayData {
                title: request.title.clone(),
                body: request.body.clone(),
                style: request.style.clone(),
                image_bgra,
                image_width,
                image_height,
            });

            let h_instance =
                windows_sys::Win32::System::LibraryLoader::GetModuleHandleW(std::ptr::null());
            let class_name: Vec<u16> = "AegisRichDisplayOverlay\0".encode_utf16().collect();
            let wc = WNDCLASSEXW {
                cbSize: std::mem::size_of::<WNDCLASSEXW>() as u32,
                style: CS_HREDRAW | CS_VREDRAW,
                lpfnWndProc: Some(rich_display_wnd_proc),
                cbClsExtra: 0,
                cbWndExtra: 0,
                hInstance: h_instance,
                hbrBackground: std::ptr::null_mut(),
                lpszMenuName: std::ptr::null(),
                lpszClassName: class_name.as_ptr(),
                hCursor: std::ptr::null_mut(),
                hIcon: std::ptr::null_mut(),
                hIconSm: std::ptr::null_mut(),
            };
            RegisterClassExW(&wc);

            let screen_w = GetSystemMetrics(SM_CXSCREEN);
            let body_lines = request.body.lines().count().max(1) as i32;
            let has_image = if let Some(ref data) = RICH_DISPLAY_DATA {
                data.image_bgra.is_some()
            } else {
                false
            };
            let wnd_w = 560;
            let image_h = if has_image { 260 } else { 0 };
            let wnd_h = std::cmp::min(760, 96 + body_lines * 24 + image_h + 44);
            let x = (screen_w - wnd_w) / 2;
            let y = 40;
            let title: Vec<u16> = "AEGIS\0".encode_utf16().collect();

            let hwnd = CreateWindowExW(
                WS_EX_TOPMOST | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW,
                class_name.as_ptr(),
                title.as_ptr(),
                WS_POPUP | WS_VISIBLE,
                x,
                y,
                wnd_w,
                wnd_h,
                std::ptr::null_mut(),
                std::ptr::null_mut(),
                h_instance,
                std::ptr::null(),
            );
            if hwnd.is_null() {
                RICH_DISPLAY_DATA = None;
                return DisplayResult {
                    shown: false,
                    response: "Failed to create overlay".to_string(),
                };
            }
            SetLayeredWindowAttributes(hwnd, 0, 235, LWA_ALPHA);
            ShowWindow(hwnd, SW_SHOWNOACTIVATE);

            let start = std::time::Instant::now();
            let duration = if request.duration_seconds == 0 {
                10
            } else {
                request.duration_seconds
            };
            let timeout = std::time::Duration::from_secs(duration as u64);
            loop {
                if start.elapsed() > timeout {
                    DestroyWindow(hwnd);
                    RICH_DISPLAY_DATA = None;
                    return DisplayResult {
                        shown: true,
                        response: "Displayed".to_string(),
                    };
                }
                let mut msg: MSG = std::mem::zeroed();
                while PeekMessageW(&mut msg, hwnd, 0, 0, PM_REMOVE) != 0 {
                    if msg.message == WM_PAINT {
                        TranslateMessage(&msg);
                        DispatchMessageW(&msg);
                    }
                }
                if GetAsyncKeyState(VK_ESCAPE as i32) as u16 & 0x8000 != 0 {
                    std::thread::sleep(std::time::Duration::from_millis(100));
                    DestroyWindow(hwnd);
                    RICH_DISPLAY_DATA = None;
                    return DisplayResult {
                        shown: true,
                        response: "Dismissed with ESC".to_string(),
                    };
                }
                std::thread::sleep(std::time::Duration::from_millis(50));
            }
        }
    }

    #[cfg(not(target_os = "windows"))]
    {
        let _ = request;
        DisplayResult {
            shown: false,
            response: "Overlay only supported on Windows".to_string(),
        }
    }
}

#[cfg(target_os = "windows")]
extern "system" fn overlay_wnd_proc(
    hwnd: windows_sys::Win32::Foundation::HWND,
    msg: u32,
    wparam: windows_sys::Win32::Foundation::WPARAM,
    lparam: windows_sys::Win32::Foundation::LPARAM,
) -> windows_sys::Win32::Foundation::LRESULT {
    unsafe {
        use windows_sys::Win32::Foundation::*;
        use windows_sys::Win32::Graphics::Gdi::*;
        use windows_sys::Win32::UI::WindowsAndMessaging::*;

        match msg {
            WM_PAINT => {
                let mut ps: PAINTSTRUCT = std::mem::zeroed();
                let hdc = BeginPaint(hwnd, &mut ps);

                let mut rect: RECT = std::mem::zeroed();
                GetClientRect(hwnd, &mut rect);

                let mem_dc = CreateCompatibleDC(hdc);
                let bmp =
                    CreateCompatibleBitmap(hdc, rect.right - rect.left, rect.bottom - rect.top);
                let old_bmp = SelectObject(mem_dc, bmp);

                let bg_brush = CreateSolidBrush(0x001B110B);
                FillRect(mem_dc, &rect, bg_brush);
                DeleteObject(bg_brush as _);

                let border_pen = CreatePen(PS_SOLID, 2, 0x004DB8FF);
                let old_pen = SelectObject(mem_dc, border_pen);
                let old_brush = SelectObject(mem_dc, GetStockObject(NULL_BRUSH));
                Rectangle(mem_dc, rect.left, rect.top, rect.right, rect.bottom);
                SelectObject(mem_dc, old_pen);
                SelectObject(mem_dc, old_brush);
                DeleteObject(border_pen as _);

                SetBkMode(mem_dc, 1);

                let title: Vec<u16> = "AEGIS Approval Required\0".encode_utf16().collect();
                SetTextColor(mem_dc, 0x004DB8FF);
                let mut title_rect = RECT {
                    left: rect.left + 16,
                    top: rect.top + 12,
                    right: rect.right - 16,
                    bottom: rect.top + 40,
                };
                DrawTextW(
                    mem_dc,
                    title.as_ptr(),
                    title.len() as i32 - 1,
                    &mut title_rect,
                    DT_LEFT | DT_SINGLELINE,
                );

                SetTextColor(mem_dc, 0x00FFF2EA);

                if let Some(ref data) = OVERLAY_DATA {
                    let action_text: Vec<u16> = format!("Action: {}\0", data.action)
                        .encode_utf16()
                        .collect();
                    let description_text: Vec<u16> = format!("Details: {}\0", data.description)
                        .encode_utf16()
                        .collect();
                    let risk_text: Vec<u16> = format!("Risk: {}\0", data.risk_level)
                        .encode_utf16()
                        .collect();

                    let mut y_pos = 48;
                    let mut line_rect = RECT {
                        left: rect.left + 16,
                        top: y_pos,
                        right: rect.right - 16,
                        bottom: y_pos + 22,
                    };
                    DrawTextW(
                        mem_dc,
                        action_text.as_ptr(),
                        action_text.len() as i32 - 1,
                        &mut line_rect,
                        DT_LEFT | DT_SINGLELINE,
                    );
                    y_pos += 24;

                    line_rect.top = y_pos;
                    line_rect.bottom = y_pos + 22;
                    DrawTextW(
                        mem_dc,
                        description_text.as_ptr(),
                        description_text.len() as i32 - 1,
                        &mut line_rect,
                        DT_LEFT | DT_SINGLELINE,
                    );
                    y_pos += 24;

                    line_rect.top = y_pos;
                    line_rect.bottom = y_pos + 22;
                    DrawTextW(
                        mem_dc,
                        risk_text.as_ptr(),
                        risk_text.len() as i32 - 1,
                        &mut line_rect,
                        DT_LEFT | DT_SINGLELINE,
                    );
                    y_pos += 28;

                    SetTextColor(mem_dc, 0x00A8D42D);
                    let approve_text: Vec<u16> = "[Y] Approve\0".encode_utf16().collect();
                    line_rect.top = y_pos;
                    line_rect.bottom = y_pos + 22;
                    DrawTextW(
                        mem_dc,
                        approve_text.as_ptr(),
                        approve_text.len() as i32 - 1,
                        &mut line_rect,
                        DT_LEFT | DT_SINGLELINE,
                    );

                    SetTextColor(mem_dc, 0x00735DFF);
                    let reject_text: Vec<u16> = "[N] Reject\0".encode_utf16().collect();
                    line_rect.left = rect.right - 120;
                    line_rect.right = rect.right - 16;
                    DrawTextW(
                        mem_dc,
                        reject_text.as_ptr(),
                        reject_text.len() as i32 - 1,
                        &mut line_rect,
                        DT_LEFT | DT_SINGLELINE,
                    );

                    SetTextColor(mem_dc, 0x008EA08B);
                    let esc_text: Vec<u16> = "[ESC] Cancel\0".encode_utf16().collect();
                    line_rect.left = rect.left + 16;
                    line_rect.right = rect.right - 16;
                    line_rect.top = y_pos + 24;
                    line_rect.bottom = y_pos + 46;
                    DrawTextW(
                        mem_dc,
                        esc_text.as_ptr(),
                        esc_text.len() as i32 - 1,
                        &mut line_rect,
                        DT_CENTER | DT_SINGLELINE,
                    );
                }

                BitBlt(
                    hdc,
                    0,
                    0,
                    rect.right - rect.left,
                    rect.bottom - rect.top,
                    mem_dc,
                    0,
                    0,
                    SRCCOPY,
                );
                SelectObject(mem_dc, old_bmp);
                DeleteObject(bmp as _);
                DeleteDC(mem_dc);

                EndPaint(hwnd, &ps);
                0
            }
            WM_ERASEBKGND => 1,
            _ => DefWindowProcW(hwnd, msg, wparam, lparam),
        }
    }
}

#[cfg(target_os = "windows")]
extern "system" fn display_wnd_proc(
    hwnd: windows_sys::Win32::Foundation::HWND,
    msg: u32,
    wparam: windows_sys::Win32::Foundation::WPARAM,
    lparam: windows_sys::Win32::Foundation::LPARAM,
) -> windows_sys::Win32::Foundation::LRESULT {
    unsafe {
        use windows_sys::Win32::Foundation::*;
        use windows_sys::Win32::Graphics::Gdi::*;
        use windows_sys::Win32::UI::WindowsAndMessaging::*;

        match msg {
            WM_PAINT => {
                let mut ps: PAINTSTRUCT = std::mem::zeroed();
                let hdc = BeginPaint(hwnd, &mut ps);

                let mut rect: RECT = std::mem::zeroed();
                GetClientRect(hwnd, &mut rect);

                let mem_dc = CreateCompatibleDC(hdc);
                let bmp =
                    CreateCompatibleBitmap(hdc, rect.right - rect.left, rect.bottom - rect.top);
                let old_bmp = SelectObject(mem_dc, bmp);

                let (bg_color, border_color, title_color) = if let Some(ref data) = DISPLAY_DATA {
                    match data.style.as_str() {
                        "warning" => (0x001A1A3E, 0x0000AAFF, 0x0000CCFF),
                        "error" => (0x001A0A0A, 0x000000FF, 0x004444FF),
                        "success" => (0x000A1A0A, 0x0000FF00, 0x0044FF44),
                        _ => (0x001E1E2E, 0x00FF8800, 0x00FF8800),
                    }
                } else {
                    (0x001E1E2E, 0x00FF8800, 0x00FF8800)
                };

                let bg_brush = CreateSolidBrush(bg_color);
                FillRect(mem_dc, &rect, bg_brush);
                DeleteObject(bg_brush as _);

                let border_pen = CreatePen(PS_SOLID, 2, border_color);
                let old_pen = SelectObject(mem_dc, border_pen);
                let old_brush = SelectObject(mem_dc, GetStockObject(NULL_BRUSH));
                Rectangle(mem_dc, rect.left, rect.top, rect.right, rect.bottom);
                SelectObject(mem_dc, old_pen);
                SelectObject(mem_dc, old_brush);
                DeleteObject(border_pen as _);

                SetBkMode(mem_dc, 1);

                if let Some(ref data) = DISPLAY_DATA {
                    SetTextColor(mem_dc, title_color);
                    let title: Vec<u16> = format!("{}\0", data.title).encode_utf16().collect();
                    let mut title_rect = RECT {
                        left: rect.left + 16,
                        top: rect.top + 12,
                        right: rect.right - 16,
                        bottom: rect.top + 38,
                    };
                    DrawTextW(
                        mem_dc,
                        title.as_ptr(),
                        title.len() as i32 - 1,
                        &mut title_rect,
                        DT_LEFT | DT_SINGLELINE,
                    );

                    SetTextColor(mem_dc, 0x00DDDDDD);
                    let mut y_pos = 44;
                    for line in data.body.lines() {
                        let text: Vec<u16> = format!("{}\0", line).encode_utf16().collect();
                        let mut line_rect = RECT {
                            left: rect.left + 20,
                            top: y_pos,
                            right: rect.right - 20,
                            bottom: y_pos + 22,
                        };
                        DrawTextW(
                            mem_dc,
                            text.as_ptr(),
                            text.len() as i32 - 1,
                            &mut line_rect,
                            DT_LEFT | DT_SINGLELINE,
                        );
                        y_pos += 24;
                    }

                    SetTextColor(mem_dc, 0x00666666);
                    let hint: Vec<u16> = "[ESC] Close\0".encode_utf16().collect();
                    let mut hint_rect = RECT {
                        left: rect.left + 16,
                        top: rect.bottom - 28,
                        right: rect.right - 16,
                        bottom: rect.bottom - 6,
                    };
                    DrawTextW(
                        mem_dc,
                        hint.as_ptr(),
                        hint.len() as i32 - 1,
                        &mut hint_rect,
                        DT_RIGHT | DT_SINGLELINE,
                    );
                }

                BitBlt(
                    hdc,
                    0,
                    0,
                    rect.right - rect.left,
                    rect.bottom - rect.top,
                    mem_dc,
                    0,
                    0,
                    SRCCOPY,
                );
                SelectObject(mem_dc, old_bmp);
                DeleteObject(bmp as _);
                DeleteDC(mem_dc);

                EndPaint(hwnd, &ps);
                0
            }
            WM_ERASEBKGND => 1,
            _ => DefWindowProcW(hwnd, msg, wparam, lparam),
        }
    }
}

#[cfg(target_os = "windows")]
extern "system" fn rich_display_wnd_proc(
    hwnd: windows_sys::Win32::Foundation::HWND,
    msg: u32,
    wparam: windows_sys::Win32::Foundation::WPARAM,
    lparam: windows_sys::Win32::Foundation::LPARAM,
) -> windows_sys::Win32::Foundation::LRESULT {
    unsafe {
        use windows_sys::Win32::Foundation::*;
        use windows_sys::Win32::Graphics::Gdi::*;
        use windows_sys::Win32::UI::WindowsAndMessaging::*;

        match msg {
            WM_PAINT => {
                let mut ps: PAINTSTRUCT = std::mem::zeroed();
                let hdc = BeginPaint(hwnd, &mut ps);
                let mut rect: RECT = std::mem::zeroed();
                GetClientRect(hwnd, &mut rect);

                let mem_dc = CreateCompatibleDC(hdc);
                let bmp =
                    CreateCompatibleBitmap(hdc, rect.right - rect.left, rect.bottom - rect.top);
                let old_bmp = SelectObject(mem_dc, bmp);

                let (bg_color, border_color, title_color) =
                    if let Some(ref data) = RICH_DISPLAY_DATA {
                        match data.style.as_str() {
                            "warning" => (0x001A1A3E, 0x0000AAFF, 0x0000CCFF),
                            "error" => (0x001A0A0A, 0x000000FF, 0x004444FF),
                            "success" => (0x000A1A0A, 0x0000FF00, 0x0044FF44),
                            _ => (0x001E1E2E, 0x00FF8800, 0x00FF8800),
                        }
                    } else {
                        (0x001E1E2E, 0x00FF8800, 0x00FF8800)
                    };

                let bg_brush = CreateSolidBrush(bg_color);
                FillRect(mem_dc, &rect, bg_brush);
                DeleteObject(bg_brush as _);

                let border_pen = CreatePen(PS_SOLID, 2, border_color);
                let old_pen = SelectObject(mem_dc, border_pen);
                let old_brush = SelectObject(mem_dc, GetStockObject(NULL_BRUSH));
                Rectangle(mem_dc, rect.left, rect.top, rect.right, rect.bottom);
                SelectObject(mem_dc, old_pen);
                SelectObject(mem_dc, old_brush);
                DeleteObject(border_pen as _);
                SetBkMode(mem_dc, 1);

                if let Some(ref data) = RICH_DISPLAY_DATA {
                    SetTextColor(mem_dc, title_color);
                    let title: Vec<u16> = format!("{}\0", data.title).encode_utf16().collect();
                    let mut title_rect = RECT {
                        left: rect.left + 16,
                        top: rect.top + 12,
                        right: rect.right - 16,
                        bottom: rect.top + 38,
                    };
                    DrawTextW(
                        mem_dc,
                        title.as_ptr(),
                        title.len() as i32 - 1,
                        &mut title_rect,
                        DT_LEFT | DT_SINGLELINE,
                    );

                    SetTextColor(mem_dc, 0x00DDDDDD);
                    let mut y_pos = 44;
                    for line in data.body.lines() {
                        let text: Vec<u16> = format!("{}\0", line).encode_utf16().collect();
                        let mut line_rect = RECT {
                            left: rect.left + 20,
                            top: y_pos,
                            right: rect.right - 20,
                            bottom: y_pos + 22,
                        };
                        DrawTextW(
                            mem_dc,
                            text.as_ptr(),
                            text.len() as i32 - 1,
                            &mut line_rect,
                            DT_LEFT | DT_SINGLELINE,
                        );
                        y_pos += 24;
                    }

                    if let Some(ref image) = data.image_bgra {
                        let max_w = rect.right - rect.left - 40;
                        let max_h = rect.bottom - y_pos - 48;
                        if max_w > 0 && max_h > 0 && data.image_width > 0 && data.image_height > 0 {
                            let scale_w = max_w as f32 / data.image_width as f32;
                            let scale_h = max_h as f32 / data.image_height as f32;
                            let scale = scale_w.min(scale_h).min(1.0);
                            let draw_w = (data.image_width as f32 * scale).max(1.0) as i32;
                            let draw_h = (data.image_height as f32 * scale).max(1.0) as i32;
                            let draw_x = rect.left + 20 + (max_w - draw_w) / 2;
                            let draw_y = y_pos + 10;

                            let mut bmi: BITMAPINFO = std::mem::zeroed();
                            bmi.bmiHeader.biSize = std::mem::size_of::<BITMAPINFOHEADER>() as u32;
                            bmi.bmiHeader.biWidth = data.image_width;
                            bmi.bmiHeader.biHeight = -data.image_height;
                            bmi.bmiHeader.biPlanes = 1;
                            bmi.bmiHeader.biBitCount = 32;
                            bmi.bmiHeader.biCompression = BI_RGB;
                            StretchDIBits(
                                mem_dc,
                                draw_x,
                                draw_y,
                                draw_w,
                                draw_h,
                                0,
                                0,
                                data.image_width,
                                data.image_height,
                                image.as_ptr() as *const _,
                                &bmi,
                                DIB_RGB_COLORS,
                                SRCCOPY,
                            );
                        }
                    }

                    SetTextColor(mem_dc, 0x00666666);
                    let hint: Vec<u16> = "[ESC] Close\0".encode_utf16().collect();
                    let mut hint_rect = RECT {
                        left: rect.left + 16,
                        top: rect.bottom - 28,
                        right: rect.right - 16,
                        bottom: rect.bottom - 6,
                    };
                    DrawTextW(
                        mem_dc,
                        hint.as_ptr(),
                        hint.len() as i32 - 1,
                        &mut hint_rect,
                        DT_RIGHT | DT_SINGLELINE,
                    );
                }

                BitBlt(
                    hdc,
                    0,
                    0,
                    rect.right - rect.left,
                    rect.bottom - rect.top,
                    mem_dc,
                    0,
                    0,
                    SRCCOPY,
                );
                SelectObject(mem_dc, old_bmp);
                DeleteObject(bmp as _);
                DeleteDC(mem_dc);
                EndPaint(hwnd, &ps);
                0
            }
            WM_ERASEBKGND => 1,
            _ => DefWindowProcW(hwnd, msg, wparam, lparam),
        }
    }
}
