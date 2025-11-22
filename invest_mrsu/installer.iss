; ==================================================================================================
; Inno Setup Script для Flutter Windows App (с проверкой VC++ Redistributable)
; Сгенерировано Manus AI
; ==================================================================================================

[Setup]
; --- Основные настройки ---
AppName=Мое Flutter Приложение
AppVersion=1.0.0
AppPublisher=Ваша Компания/Имя
AppPublisherURL=https://ваш-сайт.com
AppSupportURL=https://ваш-сайт.com/support
AppUpdatesURL=https://ваш-сайт.com/updates
DefaultDirName={autopf}\Мое Flutter Приложение
DefaultGroupName=Мое Flutter Приложение
OutputBaseFilename=Мое_Flutter_Приложение_Setup
OutputDir=.\installer_output
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=.\windows\runner\app_icon.ico ; Используем иконку из проекта Flutter
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; --- Языки ---
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

; --- Файлы приложения ---
[Files]
; Копируем ВСЕ файлы из папки релиза Flutter
Source: "build\windows\x64\release\*"
DestDir: "{app}"
Flags: ignoreversion recursesubdirs createallsubdirs

; --- Зависимости (VC++ Redistributable ) ---
; Копируем vc_redist.x64.exe во временную папку
Source: "redist\vc_redist.x64.exe"
DestDir: "{tmp}"
Flags: dontcopy

; --- Ярлыки ---
[Icons]
; Ярлык в меню "Пуск"
Name: "{group}\Мое Flutter Приложение"
Filename: "{app}\ВАШЕ_ПРИЛОЖЕНИЕ.exe"

; Ярлык на рабочем столе (опционально, с возможностью выбора)
Name: "{autodesktop}\Мое Flutter Приложение"
Filename: "{app}\ВАШЕ_ПРИЛОЖЕНИЕ.exe"
Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: Создать ярлык на рабочем столе; GroupDescription: Дополнительные задачи:;

[Run]
; --- Проверка и установка VC++ Redistributable ---
; Проверяем наличие ключа реестра для VC++ Redist 2015-2022 (x64)
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Установка необходимых компонентов Microsoft Visual C++..."; \
    Flags: skipifdoesntexist; Check: Not IsVCRedistInstalled

; Запуск приложения после установки
Filename: "{app}\ВАШЕ_ПРИЛОЖЕНИЕ.exe"; Description: Запустить Мое Flutter Приложение; Flags: postinstall nowait skipifsilent

; --- Пользовательская функция для проверки VC++ Redist ---
[Code]
// Функция для проверки наличия Microsoft Visual C++ Redistributable 2015-2022 (x64)
function IsVCRedistInstalled: Boolean;
var
  Version: String;
begin
  // Проверяем наличие ключа реестра для VC++ Redist 2015-2022 (x64)
  Result := RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64',
    'Version', Version);
end;
