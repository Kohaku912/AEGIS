Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$serviceName = "AegisPcServer"
$menu = New-Object System.Windows.Forms.ContextMenuStrip
$icon = New-Object System.Windows.Forms.NotifyIcon
$icon.Icon = [System.Drawing.SystemIcons]::Application
$icon.Text = "AEGIS PC Server"
$icon.Visible = $true

function Add-Item($Text, [scriptblock]$Action) {
    $item = New-Object System.Windows.Forms.ToolStripMenuItem
    $item.Text = $Text
    $item.add_Click($Action)
    [void]$menu.Items.Add($item)
}

Add-Item "Status" {
    $svc = Get-Service $serviceName -ErrorAction SilentlyContinue
    [System.Windows.Forms.MessageBox]::Show($(if ($svc) { "${serviceName}: $($svc.Status)" } else { "$serviceName is not installed" }))
}
Add-Item "Start" { Start-Service $serviceName -ErrorAction SilentlyContinue }
Add-Item "Stop" { Stop-Service $serviceName -ErrorAction SilentlyContinue }
Add-Item "Open Logs" { Start-Process "$env:ProgramData\AEGIS\pc-server\logs" }
Add-Item "Open Config" { Start-Process "$env:ProgramFiles\AEGIS\pc-server" }
Add-Item "Exit Tray" { $icon.Visible = $false; [System.Windows.Forms.Application]::Exit() }

$icon.ContextMenuStrip = $menu
[System.Windows.Forms.Application]::Run()
