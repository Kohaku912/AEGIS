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

# Interpreter that has grpcio-tools installed. Override when the project venv is not
# what `python` resolves to, e.g. $env:PYTHON_BIN = ".venv\Scripts\python.exe"
$PythonBin = $env:PYTHON_BIN
if (-not $PythonBin) { $PythonBin = "python" }

# Step 1: Lint
Write-Host "[1/3] buf lint..." -ForegroundColor Cyan
Push-Location $RootDir
try {
    if (Get-Command buf -ErrorAction SilentlyContinue) {
        buf lint
        Write-Host "  OK Lint passed" -ForegroundColor Green
    }
    else {
        Write-Host "  NOTE: buf not found - skipping lint" -ForegroundColor Yellow
        Write-Host "  Install: npm install -g @bufbuild/buf" -ForegroundColor Yellow
    }
}
finally { Pop-Location }

# Step 2: Generate
Write-Host "[2/3] Generating code for: $Language" -ForegroundColor Cyan
Push-Location $RootDir
try {
    # The canonical set. Every entry must exist: dev_server.proto was deleted with the
    # Dev Server but stayed in this list, so protoc failed on a missing file and the
    # script could not run at all — which is how the room server's copy drifted.
    $allProtos = @("common", "ai_server", "android_server", "room_server")

    # Servers that keep their own generated copy of the shared contract, and the protos
    # each one actually consumes. A server must not receive stubs it does not import:
    # compiling the full set into every target dropped ai_server / android_server stubs
    # into the room server, which uses neither.
    $pythonTargets = @(
        @{ OutDir = "ai-server\src\generated";   Protos = $allProtos },
        @{ OutDir = "room-server\src\generated"; Protos = @("common", "room_server") }
    )

    if ($Language -eq "python" -or $Language -eq "all") {
        foreach ($target in $pythonTargets) {
            $OutDir = $target.OutDir
            $protoPaths = @($target.Protos | ForEach-Object { "protos/aegis/$_.proto" })

            New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
            & $PythonBin -m grpc_tools.protoc -I protos --python_out=$OutDir --grpc_python_out=$OutDir --pyi_out=$OutDir $protoPaths
            if ($LASTEXITCODE -ne 0) {
                throw "grpc_tools.protoc failed with exit code $LASTEXITCODE"
            }

            # protoc emits `from aegis import ...`, but every consumer exposes the
            # stubs as the `generated.aegis` package.
            $genDir = Join-Path $OutDir "aegis"
            Get-ChildItem -Path $genDir -Recurse -File |
                Where-Object { $_.Name -like "*_pb2*" } |
                ForEach-Object {
                    $c = Get-Content $_.FullName -Raw
                    $c = $c -replace "from aegis import", "from generated.aegis import"
                    Set-Content -NoNewline -Path $_.FullName -Value $c
                }
            Write-Host "  OK Python stubs -> $OutDir" -ForegroundColor Green
        }
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
        foreach ($target in $pythonTargets) {
            $genDir = Join-Path $target.OutDir "aegis"
            if (Test-Path $genDir) {
                $count = (Get-ChildItem -Path $genDir -Filter "*_pb2*.py").Count
                Write-Host "  OK $count Python stub files in $($target.OutDir)" -ForegroundColor Green
            }
            else { Write-Host "  ERROR: No stubs found in $($target.OutDir)" -ForegroundColor Red }
        }
    }
}
finally { Pop-Location }

Write-Host "Done." -ForegroundColor Green
