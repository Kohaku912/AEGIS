!define APP_NAME "AEGIS PC Server"
!define SERVICE_NAME "AegisPcServer"
!define INSTALL_DIR "$PROGRAMFILES\AEGIS\pc-server"

Name "${APP_NAME}"
OutFile "..\..\packages\pc-server\aegis-pc-server-setup.exe"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel admin

Section "Install"
  SetOutPath "$INSTDIR"
  File "..\..\packages\pc-server\aegis-pc-server.exe"
  File "..\..\scripts\pc\install-service.ps1"
  File "..\..\scripts\pc\uninstall-service.ps1"
  ExecWait 'powershell -ExecutionPolicy Bypass -File "$INSTDIR\install-service.ps1" -InstallDir "$INSTDIR"'
  CreateShortCut "$SMPROGRAMS\AEGIS PC Server.lnk" "$INSTDIR\aegis-pc-server.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  ExecWait 'powershell -ExecutionPolicy Bypass -File "$INSTDIR\uninstall-service.ps1" -InstallDir "$INSTDIR"'
  Delete "$SMPROGRAMS\AEGIS PC Server.lnk"
  Delete "$INSTDIR\aegis-pc-server.exe"
  Delete "$INSTDIR\install-service.ps1"
  Delete "$INSTDIR\uninstall-service.ps1"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
SectionEnd
