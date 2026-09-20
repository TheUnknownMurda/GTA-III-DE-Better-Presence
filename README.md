# GTA III DE Better Presence

Detailed Discord Rich Presence for **Grand Theft Auto III – The Definitive Edition** (PC, v1.0.112):

> **Red Light District, Portland**
> ★★ · In a Banshee · Mission: Give Me Liberty
> 🕑 1:23:45 elapsed

Shows in real time: district + island, on foot / vehicle name, weapon in hand, wanted level, current mission (with its timer), pause, Wasted/Busted, menus — and, when hovering the large image, money, health and armor.

Sister project of [GTA-SA-DE-Better-Presence](https://github.com/TheUnknownMurda/GTA-SA-DE-Better-Presence) and [GTA-VC-DE-Better-Presence](https://github.com/TheUnknownMurda/GTA-VC-DE-Better-Presence): same architecture, same tooling.

## How it works

```
Game (UE4) ──UE4SS──> BetterPresence Lua mod ──> %LOCALAPPDATA%\GTAIIIDEBetterPresence\state.json
                                                          │
                          Python client (pypresence) <────┘ ──> Discord (local IPC)
```

- **`mod/BetterPresence/`** — Lua mod for [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS). Reads the game state through Unreal reflection (the `BP_GTA3Interface_C` game interface and HUD widgets) and writes a JSON file every second. No raw memory reads, no hard-coded offsets: it survives game patches better.
- **`client/`** — background Python program: detects `LibertyCity.exe`, reads the JSON and updates Discord. Falls back to a basic presence ("In game" + elapsed time) when the mod is not responding.

The mod launches the client when the game starts and the client exits by itself when the game closes, so nothing runs while you are not playing.

### Data sources (III DE 1.0.112)

| Info | Source |
|---|---|
| In game / main menu | `Gameterface:IsPlayingGame()` |
| Paused | `Gameterface.CurrentMenu` is valid |
| Position → island, district fallback | `Gameterface:GetGTAPlayerPosition()` (Unreal cm; `III_x = x/100`, `III_y = −y/100`). `client/zones.py` holds the navigation zones of the original `gta3.zon` (same boxes in the DE): the island is always known, and the district is computed from the position until the HUD has shown its name |
| District | HUD title `UI_HUDItem_TitleText_Vehicle_GTA3_C` with role `WIDGET_AREA_TEXT` (shown on every zone change, in the game's language) — takes precedence over the computed one |
| Vehicle name | The **same** widget class with role `WIDGET_VEHICLE_TEXT` (shown when entering a vehicle). Roles are captured by hooking `HUDDrawer_Base_C:CreateHudItem(For, OutItem)` (the game creates each HUD item by name); the list of known district names in 5 languages is the safety net when the role is unknown |
| Mission | HUD title `UI_HUDItem_TitleText_Mission_GTA3_C`, role `WIDGET_BIGMESSAGE_TITLE` (mission titles are upper-case in GTA III: `PAS DE SPANK POUR LA PÉPÉE` → recased by the client, see `mission_case`). Cleared on *MissionFailed*, the "Mission passed" screen, end messages going through the same widget (`MISSION PASSED!`, `RAMPAGE COMPLETE!`, `ECHEC DE LA MISSION!`…), Wasted, Busted |
| On foot / in vehicle | `Gameterface:GetAppropriateGamepadTab()` → 0 on foot, otherwise in a vehicle |
| Wanted stars | `UI_HUDItem_PlayerInfo_GTA3_C.Star1..6`: bright `Brush.TintColor` = lit star; `WantedStarsBox` hidden = 0 stars |
| Money, clock, health, armor, ammo | `MoneyText`, `TimeText`, `HealthText`, `ArmorText`, `AmmoText` of the same widget |
| Weapon in hand | `WeaponImage.Brush.ResourceObject` material name (`MI_HUD_Info_Pistol`, `MI_HUD_Info_Uzi`, `MI_HUD_Info_AK47`… named after the original game's sprites), translated in `client/gamedata.py` |
| Radio, mission timer | Titles `UI_HUDItem_TitleText_Radio_GTA3_C`, `UI_HUDItem_Timer_GTA3_C` / `UI_HUDItem_TitleText_Timer_GTA3_C` |

HUD titles are read as children of the `MainCanvas` of the two HUD drawers (`Gameterface.CurrentHudDrawer` / `CurrentPriorityHudDrawer`, classes `HUDDrawer_GTA3_C` / `PriorityHUDDrawer_GTA3_C`): ~0 ms per tick.

All of the above was validated in game on III DE 1.0.112 (`BP_GTA3Interface_C` lives in `/Game/GTA3/Maps/GTA3World/`). Should a class name change with a patch, the mod falls back to a one-time scan by pattern (`^BP_.*Interface_C$`, `^UI_HUDItem_PlayerInfo`, `^HUDDrawer_.*_C$`) and logs the class it found.

The mission-title filter (`isMissionName` in `main.lua`) discards system messages that go through the same widget.

## Installation

### 1. UE4SS in the game folder

1. Download [UE4SS v3.0.1](https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/v3.0.1) (`UE4SS_v3.0.1.zip`) and extract it into
   `…\GTA III - Definitive Edition\Gameface\Binaries\Win64\` (next to `LibertyCity.exe`).
2. Put the `UE4SS_Signatures\` folder (`StaticConstructObject.lua`, the same signature file that works for San Andreas and Vice City 1.112 — see the [SA project](https://github.com/TheUnknownMurda/GTA-SA-DE-Better-Presence#1-ue4ss-in-the-game-folder)) in the same place. Without it, UE4SS does not start on 1.112.
3. If the game folder is read-only for your account (Rockstar Games Launcher install under `Program Files`), run `tools\fix_permissions.ps1` **as administrator**: UE4SS must be able to write its log and cache there.
4. Run `tools\configure_ue4ss.ps1` (forces UE 4.26, disables the UE4SS consoles which crash this game, enables Ctrl+R hot reload, disables the bundled example mods).
5. Run `tools\install_mod.ps1`: copies `mod\BetterPresence` into `Win64\Mods\` and writes `client_path.txt` (path of the client launcher) next to it.

Check: start the game, `Win64\UE4SS.log` must contain `[BetterPresence] v… chargé` and `%LOCALAPPDATA%\GTAIIIDEBetterPresence\state.json` must be updated every second.

### 2. Discord application

1. [discord.com/developers/applications](https://discord.com/developers/applications) → *New Application*. The application **name** is what Discord shows ("Playing …").
2. Copy the *Application ID* into `client/config.json` → `discord_client_id`.
3. Optional — *Rich Presence → Art Assets*, upload images named:
   `logo` (large image), `onfoot`, `vehicle`, `menu`, `wanted_1` … `wanted_6` (small images). Ready-made icons are provided in [`assets/`](assets/) (512×512, regenerate with `tools/make_assets.py`); replace `logo` with the game cover if you like. Keys are configurable in `config.json` (`images`); a direct `https://` URL also works.
4. If Discord shows Rockstar's basic presence instead, disable the Discord integration in the Rockstar Games Launcher (or in Discord: *Settings → Registered Games*).

### 3. Python client

```bat
cd client
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
start.bat            rem console mode, logs visible
```

**Automatic lifecycle**: the mod launches the client when the game starts (`start_hidden.vbs` through `os.execute`, a console window flashes for ~100 ms) and the client exits by itself when the game closes (`exit_with_game` in `config.json`). Only one instance runs at a time (Windows mutex). Nothing runs while the game is not running. The launcher path is written by `tools\install_mod.ps1` into `Mods\BetterPresence\client_path.txt`: re-run that script if you move the project.

- `start_hidden.vbs`: manual background start, no window (handy to test without the mod).
- `stop.bat`: stops a client running in the background.
- `python presence.py --once`: prints the state read and the computed presence (debugging).
- `python presence.py --stay`: do not exit when the game closes.
- Logs: `client/presence.log`.

## Customisation

`client/config.json`:

- `texts` — displayed texts (English by default, freely translatable). `location` (line 1, `{zone}, {island}`), `location_no_island` (when the HUD district is itself an island name, e.g. "Portland"), `location_island` (position known but no district), `zones` (English computed district → your language, used until the HUD has shown the name), `on_foot_weapon` (`{transport}{sep}{weapon}`), `mission_timer`, `stats` (tooltip of the large image: a list of templates, those with a missing value are dropped)…
- `images` — asset keys; `money_format` (`{sign}${amount:,}` → `-$1,069`; use `{sign}{amount:,} $` for `1 069 $`); `mission_case` (`title` → "Don't Spank Ma Bitch Up", `sentence` → "Don't spank ma bitch up", `keep` → as displayed by the game, upper-case); `weapons` (icon → name overrides / translations); `hidden_weapons` (`["Fists"]` by default).
- Polling interval, maximum age of `state.json` before falling back to the basic presence, `exit_with_game`.

`%LOCALAPPDATA%\GTAIIIDEBetterPresence\`:

- `flags.txt` (optional, hot-reloaded by the mod) — enables/disables each data source, one `key=0|1` per line: `position`, `gamepad`, `playerinfo`, `weapon`, `titles`, `roles`, `menu`, `launch_client`, `debug` (raw details in the JSON, including the HUD item roles seen), `camera`, `misc`, `timing`, `stars_tree`, `titles_scan`.
- `zone_names.txt` (optional) — extra district names, one per line, if your game language is not among the five built in (English, French, German, Italian, Spanish — from the original game's GXT files).

## Development

- Edit `mod/BetterPresence/Scripts/main.lua`, then run `tools\install_mod.ps1` and press **Ctrl+R** in game (hot reload).
- Lua syntax check without the game: `client\.venv\Scripts\python -c "from lupa import lua54 as L; L.LuaRuntime().compile(open('mod/BetterPresence/Scripts/main.lua', encoding='utf-8').read())"` (`pip install lupa`).
- Exploration dump: create an empty `dump.request` file in the `state.json` folder → `dump_objects.txt` (classes, interesting objects, HUD item roles seen) / `dump_widgets.txt` (widgets with their role, texts, image textures). The full UE4SS dump (Ctrl+J in game → `UE4SS_ObjectDump.txt`) lists every reflected class/function.

### Known pitfalls (UE4SS 3.0.1 + the Definitive Edition)

- **`Gameterface:GetMapAreaName()` crashes the game** (crash inside UE4SS, reproduced on SA DE). Hence the district is read from the HUD title (and computed from the position as a fallback).
- **Calling a method on a null UObject crashes the game**: `pcall` does not protect against an access violation. Always check `IsValid()` first.
- `RegisterHook` on a Blueprint function (`/Game/...`) runs the callback *after* the function in 3.0.1, so out-params are readable; the function's class must already be loaded (the mod retries until the HUD drawers exist).
- `TMap` properties (`HUDDrawer_Base_C.HUDItems`) are not readable from Lua in 3.0.1 — that is why the item roles are captured with a hook instead.
- `GetAllChildren()` returns a table of `RemoteUnrealParam`: unwrap with `:get()`.
- `FindAllOf` walks the whole `GUObjectArray` (~10 ms per call): only for persistent objects, then cached.
- The UE4SS console (`ConsoleEnablerMod`, GUI) crashes this game: disabled by `configure_ue4ss.ps1`.
- `KismetSystemLibrary.LaunchURL` hands the URL to the default browser instead of executing the file: not usable to start the client, `os.execute` is the only option.

## Limitations

- The district shown in the game's language is only known after the HUD has displayed it once (game load or zone change); until then the district computed from the position (English) is shown.
- The current mission is inferred from HUD titles (start / failed / passed / death / arrest): a mission abandoned without any message may stay displayed until the next event.
- The vehicle name comes from the title shown when entering it; if it did not appear (mod loaded mid-drive), "In a vehicle" is shown.

## License

[MIT](LICENSE).
