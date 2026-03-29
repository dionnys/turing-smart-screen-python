[Setup]
; AppId asegura que se reconozca correctamente al actualizar. ¡Guarda siempre el mismo AppId para esta aplicación!
AppId={{5A1B8C9D-E0F1-2A3B-4C5D-6E7F8G9H0I1J}
AppName=TURZX 9.2 Monitor (Codeminds)
AppVersion=1.0.0
AppPublisher=Codeminds spa
AppPublisherURL=https://codeminds.cl
; Se usa {autopf} para la carpeta correcta según la arquitectura en sistemas de 64 bits
DefaultDirName={autopf}\TURZX-Monitor
DefaultGroupName=Codeminds
OutputDir=.\installer_output
OutputBaseFilename=TURZX_Monitor_Setup
Compression=lzma2/ultra64
SolidCompression=yes
; Mejoras visuales y actualizaciones
UninstallDisplayIcon={app}\main.exe
; Detiene la aplicación silenciosamente si está en ejecución durante instalación/desinstalación
CloseApplications=force
RestartApplications=no
DirExistsWarning=no
; Requerido para leer sensores CPU/GPU
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Tasks]
; Permite al usuario elegir si desea acceso directo en el escritorio en la instalación
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
; Permite elegir si inicia con Windows automáticamente (marcado por defecto)
Name: "autostart"; Description: "Ejecutar automáticamente al iniciar Windows"; GroupDescription: "Opciones de inicio:"

[Files]
; (Optimización) Usa rutas relativas para mejor portabilidad
Source: "dist\turing-system-monitor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Accesos directos para la aplicación principal
Name: "{group}\TURZX Monitor"; Filename: "{app}\main.exe"
Name: "{commondesktop}\TURZX Monitor"; Filename: "{app}\main.exe"; Tasks: desktopicon
; Accesos directos para el panel de configuración
Name: "{group}\Configurar TURZX Monitor"; Filename: "{app}\configure.exe"
Name: "{commondesktop}\Configurar TURZX Monitor"; Filename: "{app}\configure.exe"; Tasks: desktopicon

[Registry]
; Obligar a Windows a pedir permisos de Administrador (UAC) siempre que se abra el programa o su configurador
Root: HKLM; Subkey: "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"; ValueType: String; ValueName: "{app}\main.exe"; ValueData: "~ RUNASADMIN"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"; ValueType: String; ValueName: "{app}\configure.exe"; ValueData: "~ RUNASADMIN"; Flags: uninsdeletekey

[Run]
; Eliminar la tarea vieja siempre en cada instalación o actualización por si el usuario desmarcó la casilla esta vez
Filename: "schtasks"; Parameters: "/Delete /TN ""TURZX_Monitor_Autostart"" /F"; Flags: runhidden
; Crear la nueva tarea de auto-inicio SÓLO si el usuario marcó la casilla correspondiente
Filename: "schtasks"; Parameters: "/Create /F /TN ""TURZX_Monitor_Autostart"" /TR ""\""{app}\main.exe\"""" /SC ONLOGON /RL HIGHEST"; Tasks: autostart; Flags: runhidden
; Lanzar ahora (se eliminó runascurrentuser para que arranque con permisos de Admin)
Filename: "{app}\main.exe"; Description: "Lanzar monitor ahora"; Flags: nowait postinstall

[UninstallRun]
; Eliminar la tarea al desinstalar
Filename: "schtasks"; Parameters: "/Delete /TN ""TURZX_Monitor_Autostart"" /F"; Flags: runhidden