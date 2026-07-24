# 🎰 SLOT_MACHINE — Complete Instructions

Everything you need to **run the application from source**, **build the executables**, **build the iMotions launchers**, and **deploy into iMotions**.

> For *how the application works* (game logic, phases, reward maths, data schema), see **[README.md](README.md)**.

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Running from source code](#2-running-from-source-code)
3. [Choosing the language (ES / EN)](#3-choosing-the-language-es--en)
4. [Building the executables](#4-building-the-executables)
   - [4a. TEST build](#4a-test-build)
   - [4b. Production builds (the 6 real games)](#4b-production-builds-the-6-real-games)
5. [Building the iMotions launchers](#5-building-the-imotions-launchers)
   - [Path A — Python launcher `.exe`](#path-a--python-launcher-exe-recommended)
   - [Path B — BAT → Exe converter](#path-b--bat--exe-converter-backup)
   - [TEST launcher](#test-launcher)
6. [Deploying into iMotions](#6-deploying-into-imotions)
7. [Folder structure for deployment](#7-folder-structure-for-deployment)
8. [Output data (CSV)](#8-output-data-csv)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

- **Windows 10/11** (the launchers and iMotions integration are Windows-only — they use PowerShell `SendKeys`).
- **Python 3.10+**.
- A virtual environment with the project dependencies (PyQt5, pygame, pyinstaller).

```powershell
# From the project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pyqt5 pygame pyinstaller
```

> Every command below assumes the virtual environment is **activated** and you are in the **project root** (`Slot_Machine/`).

---

## 2. Running from source code

Run interactively — the terminal will prompt for the condition:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

At the prompt (`Insert CONDITION ...`), type one of:

| Input | Effect |
|-------|--------|
| `W` or `WIN`   | WIN condition — upward budget trend during bets 21–40 |
| `L` or `LOSE`  | LOSE condition — downward budget trend during bets 21–40 |
| `E` or `EQUAL` | EQUAL condition — flat budget (dev/testing only; not used in the final set) |
| `TEST W` / `TEST L` / `TEST E` | **Headless automated run** — 50 sessions × 60 bets, no user interaction |

**Syntax check without launching the GUI:**
```powershell
python -m py_compile main.py
```

**Notes when running from source:**
- No `config/build.env` exists in dev, so `BUILD_CONDITION` is `None` → the interactive prompt is used, and metrics files are named with the `MANUAL` tag (see [§8](#8-output-data-csv)).
- `MESSAGE_TYPE` in this mode comes from the default in [core/constants.py](core/constants.py) (`"MEX1"`). To try a different overlay from source, change that default temporarily.

---

## 3. Choosing the language (ES / EN)

The entire UI language is controlled by **one flag** in [utils/build_config.py](utils/build_config.py):

```python
SPANISH = True    # True  → Spanish UI
                  # False → English UI
```

- Set the flag **before building**. It is baked into the executable at build time.
- This is why the deployment tree keeps **two separate build folders**, `BUILDS/ESP/` and `BUILDS/ENG/` — one set of `.exe` files per language.
- Workflow: set `SPANISH = True`, build the set → move outputs to `BUILDS/ESP/`; set `SPANISH = False`, rebuild → move outputs to `BUILDS/ENG/`.

---

## 4. Building the executables

All build scripts live in `build/` and use **PyInstaller** (`--onefile --windowed`). They write a temporary `config/build.env` to bake the condition/message/test flags into the frozen app, then delete it afterwards.

Outputs go to `dist/`.

### 4a. TEST build

The TEST build is a short, metrics-free familiarization version (5 bets, title *"THIS IS A TEST" / "ESTO ES UNA PRUEBA"*, auto-closes). It lets a user get comfortable with the interface before a real session.

```powershell
python build/build_test.py
```

- **Output:** `dist/SlotMachine_TEST.exe`
- Writes `config/build.env` with `BUILD_CONDITION=E` + `TEST_BUILD=true` (the condition is irrelevant here — it must simply be present so the app doesn't fall back to interactive mode).
- Produces **zero CSV files** by design.

### 4b. Production builds (the 6 real games)

```powershell
python build/build_all.py
```

Builds **6 executables** — all combinations of the two used conditions (**W**, **L**) and the three message types (**MEX1**, **MEX2**, **NO_MEX**):

| Output file |
|---|
| `dist/SlotMachine_W_MEX1.exe` |
| `dist/SlotMachine_W_MEX2.exe` |
| `dist/SlotMachine_W_NO_MEX.exe` |
| `dist/SlotMachine_L_MEX1.exe` |
| `dist/SlotMachine_L_MEX2.exe` |
| `dist/SlotMachine_L_NO_MEX.exe` |

> **Why no EQUAL builds?** The `E` condition is fully implemented but was dropped from the final set, so its three entries are **commented out** in the `BUILDS` list inside [build/build_all.py](build/build_all.py). Uncomment them if you ever need the EQUAL variants.

Each build bundles the assets, styles, `redeem_codes.json`, and the generated `build.env` (containing `BUILD_CONDITION` + `MESSAGE_TYPE`), plus the full `pygame` package.

> 🌍 Remember to set the `SPANISH` flag (see [§3](#3-choosing-the-language-es--en)) **before** each run, and keep the ES and EN outputs in separate folders.

---

## 5. Building the iMotions launchers

**Why a launcher at all?** iMotions can only launch an item by an **`.exe` path**, and after that item exits it needs a keystroke to advance to the next page. A launcher is a tiny wrapper that:

1. Launches the target slot-machine `.exe`.
2. **Blocks until that `.exe` exits** (for any reason).
3. Sends **Shift + Page Down** to iMotions, advancing it to the next page.

There are **two ways** to produce a launcher. Both implement the exact same behaviour (`LAUNCHER_TEMPLATE`).

### Path A — Python launcher `.exe` (recommended)

A fully self-contained PyInstaller executable that embeds the launcher logic and the target's name.

```powershell
python build/build_all_launchers.py
```

For each of the 6 production builds this generates, in `dist/`:
- `launcher_{W|L}_{MEX1|MEX2|NO_MEX}.exe` — the ready-to-use launcher (no console window).
- `bat_launcher_{W|L}_{MEX1|MEX2|NO_MEX}.bat` — a `.bat` **backup** with identical behaviour (see Path B).

Each launcher targets its matching build by name (e.g. `launcher_W_MEX1.exe` → `SlotMachine_W_MEX1.exe`) and expects that `.exe` to sit **in the same folder**.

### Path B — BAT → Exe converter (backup)

`build_all_launchers.py` also writes a `.bat` version of every launcher. iMotions does not accept `.bat` paths directly, so if you use this route you must convert each `.bat` into an `.exe` with a **Bat-to-Exe converter** tool, then register that `.exe` in iMotions.

The `.bat` logic is:
```bat
@echo off
cd /d "%~dp0"
start /wait "" "%~dp0SlotMachine_X_Y.exe"
timeout /t 1 /nobreak >nul
powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('+{PGDN}')"
```

> A standalone reference copy lives at [build/bat_launcher_backup.bat](build/bat_launcher_backup.bat). Path A is preferred; Path B exists only as a fallback.

### TEST launcher

The TEST build has its **own dedicated launcher script**, [imotions_launcher.py](imotions_launcher.py), whose logic mirrors the template exactly but is hardcoded to target `SlotMachine_TEST.exe`. Build it with:

```powershell
python build/build_imotions_launcher.py
```

- **Output:** `dist/imotions_launcher.exe`
- Runs `SlotMachine_TEST.exe`, waits, then sends Shift + Page Down — same as the production launchers.

> There is also a simpler root-level [app_launcher.py](app_launcher.py) that only runs `SlotMachine_TEST.exe` **without** sending the keystroke. It is a bare backup, **not** the iMotions launcher — use `build_imotions_launcher.py` for iMotions.

---

## 6. Deploying into iMotions

For each condition you want to present:

1. **Pick the language** (`BUILDS/ENG/` or `BUILDS/ESP/`) and the variant you need.
2. **Copy the slot-machine `.exe`** into the matching `LAUNCHERS/` subfolder — the launcher and its target **must live in the same folder**:

   | Application build | Copy into |
   |---|---|
   | `SlotMachine_W_MEX1.exe`  | `LAUNCHERS/W_MEX1/` |
   | `SlotMachine_W_MEX2.exe`  | `LAUNCHERS/W_MEX2/` |
   | `SlotMachine_W_NO_MEX.exe` | `LAUNCHERS/W_NO_MEX/` |
   | `SlotMachine_L_MEX1.exe`  | `LAUNCHERS/L_MEX1/` |
   | `SlotMachine_L_MEX2.exe`  | `LAUNCHERS/L_MEX2/` |
   | `SlotMachine_L_NO_MEX.exe` | `LAUNCHERS/L_NO_MEX/` |
   | `SlotMachine_TEST.exe`    | `LAUNCHERS/TEST/` |

3. In iMotions, add the **launcher `.exe`** (Path A) — or your converted Bat-to-Exe (Path B) — as the item for that condition. Do **not** point iMotions at the slot-machine `.exe` directly, or it will never advance to the next page.

**What the launcher does automatically:** starts the slot machine → waits for it to finish → sends Shift + Page Down to move iMotions on.

---

## 7. Folder structure for deployment

```
SLOT_MACHINE/
  BUILDS/
    ENG/          → all English application builds (.exe)   (SPANISH = False)
    ESP/          → all Spanish application builds (.exe)   (SPANISH = True)
  LAUNCHERS/
    W_MEX1/       → launcher + its SlotMachine_W_MEX1.exe
    W_MEX2/
    W_NO_MEX/
    L_MEX1/
    L_MEX2/
    L_NO_MEX/
    TEST/         → imotions_launcher.exe + SlotMachine_TEST.exe
```

Inside each `LAUNCHERS/` subfolder pick **one** launcher:

| File | Notes |
|---|---|
| `launcher_X_Y.exe` | PyInstaller build (Path A) — no console window |
| `bat_launcher_X_Y.exe` | Bat-to-Exe build (Path B) — no console window |

**Replacing a build:** just drop the new `.exe` into the correct `LAUNCHERS/` subfolder. The launchers never need to be rebuilt or reconfigured — they find the target by name in their own folder.

---

## 8. Output data (CSV)

Production builds write append-only CSV files to a writable `data/` folder next to the executable:

```
metrics_{CONDITION}_{MESSAGE}_{INDEX}.csv
```
- `{CONDITION}` = `W` / `L` / `E`, or **`MANUAL`** when run unbaked from source.
- `{MESSAGE}` = `MEX1` / `MEX2` / **`NO_MEX`**.
- `{INDEX}` auto-increments per run (`_1`, `_2`, …) so nothing is overwritten.

**The TEST build writes no CSV at all** — it is completely isolated from metrics.

Schema and event types are documented in **[README.md](README.md#-data-collection--coremetrics_loggerpy)**.

> ⚠️ A BET row is logged **at the end of the reel animation**, not on click. If the app is force-closed mid-spin, that final bet is not recorded (only `SESSION_END` is written).

---

## 9. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| App opens but immediately asks for a condition in a build | `config/build.env` was missing/empty during the build → `BUILD_CONDITION` fell back to `None`. Rebuild with the proper script. |
| iMotions never advances after the game | You pointed iMotions at the slot-machine `.exe` instead of the **launcher** `.exe`. Use the launcher. |
| Launcher can't find the game | The slot-machine `.exe` is not in the **same folder** as the launcher. See a `launcher_error.log` written next to the launcher. |
| Wrong UI language | `SPANISH` flag was set incorrectly **before building**. Fix the flag in [utils/build_config.py](utils/build_config.py) and rebuild. |
| Countdown never unlocks the CLOSE button (MEX2) | Expected — MEX2 locks CLOSE for `MESSAGE_TIMER = 180` seconds by design. |
| No CSV produced | Either it's the TEST build (intended), or metrics were never enabled — check that `start_metrics()` ran (it is skipped in TEST mode only). |
| A frozen build can't find assets | All asset access must go through `utils.file_manager.get_path(...)`; a raw `open("gui/...")` breaks in the `.exe` because the CWD is not the project root. |
