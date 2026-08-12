//! Windows UI Automation tree capture (UIA via PowerShell interop).

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct UiNode {
    pub name: String,
    pub automation_id: String,
    pub control_type: String,
    pub bounds: [i32; 4],
    pub is_enabled: bool,
    pub is_password: bool,
    #[serde(default)]
    pub children: Vec<UiNode>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UiTree {
    pub ui_tree: UiNode,
}

/// Capture the foreground window UI tree (Windows UIA).
pub fn get_ui_tree(include_invisible: bool) -> Result<UiTree, String> {
    #[cfg(target_os = "windows")]
    {
        let flag = if include_invisible { "true" } else { "false" };
        let script = format!(
            r#"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
function Get-UiNode($el, $depth) {{
  if ($depth -gt 6) {{ return $null }}
  $rect = $el.Current.BoundingRectangle
  $node = [ordered]@{{
    name = [string]$el.Current.Name
    automation_id = [string]$el.Current.AutomationId
    control_type = [string]$el.Current.ControlType.ProgrammaticName
    bounds = @([int]$rect.X,[int]$rect.Y,[int]$rect.Width,[int]$rect.Height)
    is_enabled = [bool]$el.Current.IsEnabled
    is_password = [bool]$el.Current.IsPassword
    children = @()
  }}
  if (-not ${flag}) {{
    if (-not $el.Current.IsOffscreen -and $rect.Width -le 0 -and $rect.Height -le 0) {{ return $null }}
  }}
  foreach ($child in $el.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {{
    $c = Get-UiNode $child ($depth + 1)
    if ($null -ne $c) {{ $node.children += $c }}
  }}
  return $node
}}
$root = [System.Windows.Automation.AutomationElement]::FocusedElement
if ($null -eq $root) {{ $root = [System.Windows.Automation.AutomationElement]::RootElement }}
$tree = Get-UiNode $root 0
@{{ ui_tree = $tree }} | ConvertTo-Json -Depth 12 -Compress
"#
        );
        let output = std::process::Command::new("powershell")
            .args(["-NoProfile", "-NonInteractive", "-Command", &script])
            .output()
            .map_err(|e| format!("UIA capture failed: {e}"))?;
        if !output.status.success() {
            return Err(String::from_utf8_lossy(&output.stderr).to_string());
        }
        let stdout = String::from_utf8_lossy(&output.stdout);
        serde_json::from_str(&stdout).map_err(|e| format!("UIA JSON parse failed: {e}"))
    }

    #[cfg(not(target_os = "windows"))]
    {
        let _ = include_invisible;
        Ok(UiTree {
            ui_tree: UiNode {
                name: "desktop".into(),
                automation_id: "".into(),
                control_type: "Pane".into(),
                bounds: [0, 0, 0, 0],
                is_enabled: true,
                is_password: false,
                children: vec![],
            },
        })
    }
}

/// Find a UI node by automation id or name substring.
pub fn find_ui_element(query: &str) -> Result<serde_json::Value, String> {
    let tree = get_ui_tree(false)?;
    fn walk(node: &UiNode, query: &str, hits: &mut Vec<&UiNode>) {
        if node.automation_id.contains(query) || node.name.contains(query) {
            hits.push(node);
        }
        for child in &node.children {
            walk(child, query, hits);
        }
    }
    let mut hits = Vec::new();
    walk(&tree.ui_tree, query, &mut hits);
    Ok(serde_json::json!({ "matches": hits }))
}
