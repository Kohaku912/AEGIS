# AEGIS PC Server Production Packaging

## Default Bind

Production PC Server should bind to `127.0.0.1` by default. Use a Tailscale or
VPN interface address only when another trusted AEGIS host must connect.
Avoid `0.0.0.0` outside isolated lab networks.

## Portable Package

Build:

```powershell
.\scripts\pc\build-portable.ps1
```

The portable config uses `bind=127.0.0.1`. Change it only for VPN-scoped
deployments.

## Windows Service

Install and start:

```powershell
.\scripts\pc\install-service.ps1 -Bind 127.0.0.1 -Port 50052
```

Logs are written to:

```text
%ProgramData%\AEGIS\pc-server\logs\stdout.log
%ProgramData%\AEGIS\pc-server\logs\stderr.log
```

Real click/type/hotkey actions require the explicit `-EnableRealPcActions`
installer flag and the E2E runner flag.

Uninstall:

```powershell
.\scripts\pc\uninstall-service.ps1
```

## Real E2E

```powershell
.\scripts\e2e\run-pc-real.ps1 -InstallService -RealActions -UninstallAfter
```

For reboot validation, install without `-UninstallAfter`, reboot Windows,
confirm `AegisPcServer` is `Running`, then run the E2E runner again without
`-InstallService`.

## Installer Path

NSIS is the default consumer installer path for the next phase. It should place
the binary, create the config/log directories, register the service, add the
firewall rule, create shortcuts/tray registration, and uninstall cleanly. MSI or
WiX remains the enterprise packaging option if managed deployment becomes
required.
