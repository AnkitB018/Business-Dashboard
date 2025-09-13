; Business Dashboard Installer Script
; NSIS (Nullsoft Scriptable Install System) script for creating a proper installer

!define APP_NAME "Business Dashboard"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Antrocraft and Arolive Build"
!define APP_URL "https://github.com/AnkitB018/Business-Dashboard"
!define APP_SUPPORT_URL "mailto:support@businessdashboard.com"
!define APP_UNINSTALL_KEY "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BusinessDashboard"

; Include modern UI
!include "MUI2.nsh"
!include "FileFunc.nsh"

; General settings
Name "${APP_NAME}"
OutFile "BusinessDashboard_Installer.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"
InstallDirRegKey HKLM "${APP_UNINSTALL_KEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor lzma

; Version information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "© 2025 ${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "FileVersion" "1.0.0.0"

; Interface configuration
!define MUI_ABORTWARNING
; !define MUI_ICON "icon.ico"
; !define MUI_UNICON "icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
; !define MUI_HEADERIMAGE_BITMAP "header.bmp"
; !define MUI_WELCOMEFINISHPAGE_BITMAP "welcome.bmp"
; !define MUI_UNWELCOMEFINISHPAGE_BITMAP "welcome.bmp"

; License settings
!define MUI_LICENSEPAGE_CHECKBOX

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page - use absolute path to LICENSE.md
!insertmacro MUI_PAGE_LICENSE "..\LICENSE.md"

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Start menu page
Var StartMenuFolder
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${APP_UNINSTALL_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

; Installation page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\\BusinessDashboard.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"
!define MUI_FINISHPAGE_LINK "Visit our website"
!define MUI_FINISHPAGE_LINK_LOCATION "${APP_URL}"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installation sections
Section "Core Application" SecCore
    SectionIn RO  ; Read-only (required)
    
    ; Set output path to the installation directory
    SetOutPath "$INSTDIR"
    
    ; Files to install
    File /r "installer\\app\\BusinessDashboard\\*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; Store installation folder
    WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "InstallLocation" $INSTDIR
    
    ; Create registry entries
    WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "URLInfoAbout" "${APP_URL}"
    WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "HelpLink" "${APP_SUPPORT_URL}"
    WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "QuietUninstallString" "$INSTDIR\\Uninstall.exe /S"
    WriteRegDWORD HKLM "${APP_UNINSTALL_KEY}" "NoModify" 1
    WriteRegDWORD HKLM "${APP_UNINSTALL_KEY}" "NoRepair" 1
    
    ; Calculate and store installed size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "${APP_UNINSTALL_KEY}" "EstimatedSize" "$0"
    
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortcut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\BusinessDashboard.exe" "" "$INSTDIR\\BusinessDashboard.exe" 0
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    CreateDirectory "$SMPROGRAMS\\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\\$StartMenuFolder\\${APP_NAME}.lnk" "$INSTDIR\\BusinessDashboard.exe" "" "$INSTDIR\\BusinessDashboard.exe" 0
    CreateShortcut "$SMPROGRAMS\\$StartMenuFolder\\Uninstall ${APP_NAME}.lnk" "$INSTDIR\\Uninstall.exe" "" "$INSTDIR\\Uninstall.exe" 0
    
    !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "Database Configuration" SecDatabase
    ; Launch database configuration on first run
    WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "FirstRun" "1"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core application files (required)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create a desktop shortcut"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Create Start Menu shortcuts"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDatabase} "Configure database connection on first run"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Installation functions
Function .onInit
    ; Check if already installed
    ReadRegStr $0 HKLM "${APP_UNINSTALL_KEY}" "UninstallString"
    StrCmp $0 "" proceed
    
    MessageBox MB_YESNO|MB_ICONQUESTION "${APP_NAME} is already installed. Do you want to uninstall the previous version?" IDYES uninstall IDNO abort
    
    uninstall:
        ExecWait '$0 /S _?=$INSTDIR'
        Goto proceed
    
    abort:
        Abort "Installation cancelled by user."
    
    proceed:
FunctionEnd

Function .onInstSuccess
    ; Check if this is a first-time installation
    ReadRegStr $0 HKLM "${APP_UNINSTALL_KEY}" "FirstRun"
    StrCmp $0 "1" showConfig skipConfig
    
    showConfig:
        MessageBox MB_YESNO "Installation complete! Do you want to configure the database connection now?" IDYES runConfig IDNO skipConfig
        
        runConfig:
            Exec '"$INSTDIR\\python.exe" "$INSTDIR\\database_config.py"'
        
    skipConfig:
        ; Remove first run flag
        DeleteRegValue HKLM "${APP_UNINSTALL_KEY}" "FirstRun"
FunctionEnd

; Uninstallation section
Section "Uninstall"
    ; Remove files and directories
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    Delete "$SMPROGRAMS\\$StartMenuFolder\\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\\$StartMenuFolder\\Uninstall ${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\\$StartMenuFolder"
    Delete "$DESKTOP\\${APP_NAME}.lnk"
    
    ; Remove registry entries
    DeleteRegKey HKLM "${APP_UNINSTALL_KEY}"
    
    ; Ask about user data
    MessageBox MB_YESNO "Do you want to remove user data and configuration files?" IDYES removeUserData IDNO skipUserData
    
    removeUserData:
        RMDir /r "$PROFILE\\BusinessDashboard"
    
    skipUserData:
    
SectionEnd

; Uninstaller functions
Function un.onInit
    MessageBox MB_YESNO "Are you sure you want to completely remove ${APP_NAME} and all of its components?" IDYES proceed IDNO abort
    proceed:
        Return
    abort:
        Abort
FunctionEnd
