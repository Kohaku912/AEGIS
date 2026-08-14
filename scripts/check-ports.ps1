# check-ports.ps1 — Check AEGIS service ports
#
# Usage:
#   .\scripts\check-ports.ps1

$ports = @(
    @{Port=50051; Name="AI Server (gRPC)"},
    @{Port=50052; Name="PC Server (health)"},
    @{Port=50053; Name="Browser Server (gRPC)"},
    @{Port=8090;  Name="Dashboard"},
    @{Port=8080;  Name="Approval UI"}
)

Write-Host ""
Write-Host "AEGIS Port Status" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host ""

foreach ($p in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $p.Port -ErrorAction SilentlyContinue
    if ($conn) {
        $procId = $conn[0].OwningProcess
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        $procName = if ($proc) { $proc.ProcessName } else { "unknown" }
        Write-Host "  [OPEN]  $($p.Port) - $($p.Name) (PID: $procId, $procName)" -ForegroundColor Green
    } else {
        Write-Host "  [----]  $($p.Port) - $($p.Name)" -ForegroundColor Gray
    }
}

Write-Host ""
