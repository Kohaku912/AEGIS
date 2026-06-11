# generate_protos.ps1 — PowerShell script for proto code generation
# Usage: .\scripts\generate_protos.ps1 [-Language python|node|kotlin|all]
#
# Prerequisites:
#   Python: pip install grpcio-tools
#   buf:    npm install -g @bufbuild/buf

param(
    [string]$Language = "python"
)

$ErrorActionPreference = "Stop"
$RootDir = $PWD

# Step 1: Lint
Write-Host "[1/3] buf lint..." -ForegroundColor Cyan
Push-Location $RootDir
try { buf lint; Write-Host "  OK Lint passed" -ForegroundColor Green }
finally { Pop-Location }

# Step 2: Generate
Write-Host "[2/3] Generating code for: $Language" -ForegroundColor Cyan
Push-Location $RootDir
try {
    $protoList = @(
        "protos/aegis/common.proto",
        "protos/aegis/ai_server.proto",
        "protos/aegis/pc_server.proto",
        "protos/aegis/android_server.proto",
        "protos/aegis/browser_server.proto",
        "protos/aegis/room_server.proto",
        "protos/aegis/dev_server.proto"
    )

    if ($Language -eq "python" -or $Language -eq "all") {
        $OutDir = "ai-server\src\generated"
        New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
        python -m grpc_tools.protoc -I protos --python_out=$OutDir --grpc_python_out=$OutDir --pyi_out=$OutDir $protoList

        # Fix generated imports
        $genDir = Join-Path $OutDir "aegis"
        Get-ChildItem -Path $genDir -Filter "*_pb2*.py" | ForEach-Object {
            $c = Get-Content $_.FullName -Raw
            $c = $c -replace "from aegis import", "from generated.aegis import"
            Set-Content -NoNewline -Path $_.FullName -Value $c
        }
        Write-Host "  OK Python stubs -> $OutDir" -ForegroundColor Green
    }

    if ($Language -eq "node" -or $Language -eq "all") {
        Write-Host "  NOTE: Node.js generation requires grpc-tools npm package." -ForegroundColor Yellow
        Write-Host "  See docs/proto-build.md for instructions." -ForegroundColor Yellow
    }

    if ($Language -eq "kotlin" -or $Language -eq "all") {
        Write-Host "  NOTE: Kotlin generation uses Gradle protobuf plugin." -ForegroundColor Yellow
        Write-Host "  See docs/proto-build.md for instructions." -ForegroundColor Yellow
    }
}
finally { Pop-Location }

# Step 3: Verify
Write-Host "[3/3] Verification..." -ForegroundColor Cyan
Push-Location $RootDir
try {
    if ($Language -eq "python" -or $Language -eq "all") {
        $genDir = "ai-server\src\generated\\aegis"
        if (Test-Path $genDir) {
            $count = (Get-ChildItem -Path $genDir -Filter "*_pb2*.py").Count
            Write-Host "  OK $count Python stub files" -ForegroundColor Green
        }
        else { Write-Host "  ERROR: No stubs found" -ForegroundColor Red }
    }
}
finally { Pop-Location }

Write-Host "Done." -ForegroundColor Green
