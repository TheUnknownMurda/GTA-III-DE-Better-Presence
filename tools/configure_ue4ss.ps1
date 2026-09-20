# Applique la configuration UE4SS qui fonctionne avec GTA III DE 1.0.112 :
#   - UE4SS-settings.ini : moteur forcé en 4.26, consoles UE4SS désactivées (plantent sur ce jeu),
#     hot reload activé (Ctrl+R), GraphicsAPI dx11
#   - Mods\mods.txt      : tous les mods livrés avec UE4SS désactivés sauf Keybinds
# Idempotent. Une sauvegarde .bak est créée au premier passage.

param(
    [string]$GameWin64 = "E:\Program Files\Rockstar Games\GTA III - Definitive Edition\Gameface\Binaries\Win64"
)

$ErrorActionPreference = "Stop"

function Read-Utf8($path) {
    $bytes = [IO.File]::ReadAllBytes($path)
    $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    $text = [Text.Encoding]::UTF8.GetString($bytes)
    if ($text.StartsWith([char]0xFEFF)) { $text = $text.Substring(1) }
    return @{ Text = $text; Bom = $bom; Nl = $(if ($text -match "`r`n") { "`r`n" } else { "`n" }) }
}

function Write-Utf8($path, $text, $bom) {
    [IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($bom))
}

function Backup-Once($path) {
    $bak = "$path.bak"
    if (-not (Test-Path $bak)) { Copy-Item $path $bak }
}

# --- UE4SS-settings.ini ---------------------------------------------------
$ini = Join-Path $GameWin64 "UE4SS-settings.ini"
if (-not (Test-Path $ini)) { Write-Error "Introuvable : $ini (UE4SS n'est pas installé ?)"; exit 1 }
Backup-Once $ini
$f = Read-Utf8 $ini
$wanted = @(
    @("EngineVersionOverride", "MajorVersion", "4"),
    @("EngineVersionOverride", "MinorVersion", "26"),
    @("General", "EnableHotReloadSystem", "1"),
    @("Debug", "ConsoleEnabled", "0"),
    @("Debug", "GuiConsoleEnabled", "0"),
    @("Debug", "GuiConsoleVisible", "0"),
    @("Debug", "GraphicsAPI", "dx11")
)
$lines = $f.Text -split $f.Nl
$section = ""
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\[(.+)\]\s*$') { $section = $Matches[1]; continue }
    foreach ($w in $wanted) {
        if ($section -eq $w[0] -and $lines[$i] -match ('^\s*' + [regex]::Escape($w[1]) + '\s*=')) {
            $lines[$i] = "$($w[1]) = $($w[2])"
        }
    }
}
Write-Utf8 $ini ($lines -join $f.Nl) $f.Bom
Write-Host "UE4SS-settings.ini configuré."

# --- mods.txt -------------------------------------------------------------
$mt = Join-Path $GameWin64 "Mods\mods.txt"
if (Test-Path $mt) {
    Backup-Once $mt
    $f = Read-Utf8 $mt
    $lines = $f.Text -split $f.Nl | ForEach-Object {
        if ($_ -match '^(\w+)\s*:\s*\d\s*$' -and $Matches[1] -ne "Keybinds") { "$($Matches[1]) : 0" } else { $_ }
    }
    Write-Utf8 $mt ($lines -join $f.Nl) $f.Bom
    Write-Host "mods.txt : mods UE4SS livrés désactivés (sauf Keybinds)."
}

Write-Host "Terminé. Le mod BetterPresence est activé par son fichier enabled.txt (voir install_mod.ps1)."
