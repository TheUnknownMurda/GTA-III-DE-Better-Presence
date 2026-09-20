# Copie (ou met à jour) le mod UE4SS BetterPresence dans le dossier Mods du jeu.
# Relance ce script après chaque modification de mod\BetterPresence\Scripts\main.lua,
# puis appuie sur Ctrl+R en jeu (hot reload UE4SS) ou relance le jeu.
#
# Le mod est activé par le fichier mod\BetterPresence\enabled.txt (mécanisme UE4SS) :
# pas besoin de le déclarer dans mods.txt.

param(
    [string]$GameWin64 = "E:\Program Files\Rockstar Games\GTA III - Definitive Edition\Gameface\Binaries\Win64"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$src  = Join-Path $root "mod\BetterPresence"
$dst  = Join-Path $GameWin64 "Mods\BetterPresence"

if (-not (Test-Path (Join-Path $GameWin64 "UE4SS.dll"))) {
    Write-Error "UE4SS.dll introuvable dans $GameWin64 - installe UE4SS d'abord (voir README)."
    exit 1
}
if (-not (Test-Path $src)) {
    Write-Error "Source introuvable : $src"
    exit 1
}

New-Item -ItemType Directory -Force -Path $dst | Out-Null
Copy-Item -Path (Join-Path $src "*") -Destination $dst -Recurse -Force

# Chemin du lanceur du client Discord : le mod le lit au démarrage du jeu et
# lance le client (os.execute -> wscript, sans console).
$launcher = Join-Path $root "client\start_hidden.vbs"
if (Test-Path $launcher) {
    [IO.File]::WriteAllText((Join-Path $dst "client_path.txt"), $launcher, [Text.UTF8Encoding]::new($false))
} else {
    Write-Warning "client\start_hidden.vbs introuvable : le client ne sera pas lancé automatiquement."
}

Write-Host "Mod installé dans $dst"
Get-ChildItem -Recurse -File $dst | ForEach-Object { "  " + $_.FullName.Substring($dst.Length + 1) + "  (" + $_.Length + " o)" }
