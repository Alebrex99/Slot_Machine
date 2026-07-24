# 🎰 Slot Machine — In-Depth Technical Reference (`README_DEPTH.md`)

This is the **exhaustive** developer reference. It walks through the system **in execution order**, starting from `main.py`, explaining *how each component works internally*, *why it is built that way*, and *how the pieces talk to each other* — including a full, detailed treatment of the **build system**.

- For a **conceptual overview** (what the experiment is, phases, reward maths at a glance) → [README.md](README.md).
- For **operational how-to** (run, build, deploy into iMotions) → [INSTRUCTIONS.md](INSTRUCTIONS.md).
- This document is the **why & how of the internals**.

---

## Table of Contents

1. [Bird's-eye data flow](#1-birds-eye-data-flow)
2. [Startup sequence — `main.py`](#2-startup-sequence--mainpy)
3. [Configuration layer — `build_config.py` + `constants.py`](#3-configuration-layer--build_configpy--constantspy)
4. [Path resolution — `utils/file_manager.py`](#4-path-resolution--utilsfile_managerpy)
5. [The researcher authority — `core/remote_researcher.py`](#5-the-researcher-authority--coreremote_researcherpy)
6. [The reward engine — `core/slot_logic.py`](#6-the-reward-engine--coreslot_logicpy)
7. [Metrics & CSV — `core/metrics_logger.py`](#7-metrics--csv--coremetrics_loggerpy)
8. [The GUI & session loop — `gui/main_window.py`](#8-the-gui--session-loop--guimain_windowpy)
9. [The message overlay — `gui/message_window.py`](#9-the-message-overlay--guimessage_windowpy)
10. [Redeem subsystem — `redeem_logic.py` + `redeem_dialog.py`](#10-redeem-subsystem--redeem_logicpy--redeem_dialogpy)
11. [Audio — `core/sound_manager.py`](#11-audio--coresound_managerpy)
12. [**The build system in depth**](#12-the-build-system-in-depth)
13. [Test mode internals](#13-test-mode-internals)
14. [Critical invariants recap](#14-critical-invariants-recap)

---

## 1. Bird's-eye data flow

```
                         ┌────────────────────────────────────────────┐
                         │                 main.py                      │
                         │  (reads baked config, wires the 3 objects)   │
                         └───────────────┬──────────────────────────────┘
                                         │
     build_config.py ──reads──► config/build.env ──(frozen only)         │ creates, in order:
     (BUILD_CONDITION,                                                    ▼
      MESSAGE_TYPE,           ┌───────────────────┐   ┌────────────────────┐   ┌───────────────┐
      IS_TEST_BUILD,          │  MetricsLogger    │   │  RemoteResearcher  │   │  MainWindow   │
      SPANISH)                │  (CSV lifecycle)  │◄──│ (sets condition,   │   │  (GUI + loop) │
                              └─────────┬─────────┘   │  enables metrics)  │   └───────┬───────┘
                                        │             └─────────┬──────────┘           │
                                        │  log_bet/session      │ update_condition()   │ on_spin()
                                        ▼                       ▼                      ▼
                               data/metrics_*.csv        core/slot_logic.py  ◄── calculate_reward()
                                                          (deterministic          spin_reels()
                                                           reward engine)
```

**One-line summary:** `build_config` decides *what kind of session this is*, `RemoteResearcher` *arms* it, `MainWindow` *runs* it, `slot_logic` *decides every outcome*, and `MetricsLogger` *records* it.

---

## 2. Startup sequence — `main.py`

Execution order when the app launches (dev **or** frozen `.exe`):

1. **Imports trigger config resolution.** The line `from utils.build_config import BUILD_CONDITION, IS_TEST_BUILD, MESSAGE_TYPE` causes `build_config.py` to run *at import time* — it reads `config/build.env` (if present) and freezes the four module-level constants before any window exists. This is the linchpin: **all downstream behaviour is decided here, once.**

2. **Debug log written.** `main.py` writes an `app_debug.log` next to the executable capturing `sys.executable`, the resolved data path, and the three baked config values. This is deliberately a *file* (not just stdout) because `--windowed` PyInstaller builds have no console — it's the only way to diagnose a misbehaving frozen build in the field.

3. **`QApplication` + stylesheet.** `load_stylesheet()` reads the QSS via `get_path("gui","styles","style.qss")` — note it uses `get_path`, **not** a raw `open("gui/styles/...")`, because in a frozen exe the working directory is *not* the project root (see §4).

4. **`MetricsLogger` is constructed** with `is_test_build=IS_TEST_BUILD`. In a normal build this immediately computes the next CSV filename and writes the header row; in a TEST build it creates *nothing* (see §7).

5. **`RemoteResearcher` is constructed** with the logger injected.

6. **Condition is armed — two paths:**
   ```python
   if BUILD_CONDITION is not None:          # frozen production build
       remote_researcher.set_condition(BUILD_CONDITION)
       if not IS_TEST_BUILD:
           remote_researcher.start_metrics()
   else:                                     # dev / manual mode
       remote_researcher.set_input_data()    # interactive terminal prompt
       if not IS_TEST_BUILD:
           remote_researcher.start_metrics()
   ```
   - **Frozen build:** condition is baked in → prompt is skipped.
   - **Dev/manual:** the terminal prompts for `W`/`L`/`E` or `TEST <cond>`.
   - `start_metrics()` is guarded by `if not IS_TEST_BUILD` — **this is the single point that keeps a TEST build from ever enabling logging.**

7. **`MainWindow` is created and shown.**

8. **If TEST mode was requested** (`remote_researcher.test_mode` is `True`, only reachable via a `TEST <cond>` prompt), `window.testing_statistics_v2(...)` runs the automated 50×60 headless playthrough *before* `app.exec_()` blocks.

9. **`sys.exit(app.exec_())`** enters the Qt event loop.

> **Key insight:** the whole "what session is this?" decision is data-driven from a single bundled file, resolved at import time. There is no runtime branching on build type scattered through the code — everything reads the same four constants.

---

## 3. Configuration layer — `build_config.py` + `constants.py`

Two files cooperate to produce the four runtime flags. The rule enforced throughout the codebase: **always import these from `utils.build_config`, never from `core.constants`.**

### `core/constants.py` — the defaults & static data
Holds every shared constant with **no internal imports** (so it can never cause a circular import). It defines:
- The dev **defaults** `BUILD_CONDITION = None` and `MESSAGE_TYPE = "MEX1"`.
- Game constants (`INITIAL_BUDGET`, bet bounds, `TOTAL_SESSION_BETS`, `PHASE_LENGTH`, `MESSAGE_TIMER`, `TOTAL_TESTS`, …).
- `VALID_CONDITIONS = {"E":"EQUAL", "W":"WIN", "L":"LOSE"}`.
- `PHASES` (the three global bet-number ranges).
- The static data tables: `SYMBOLS`, `REWARD_TABLE_MUL`, `EXPECTED_PERCENTAGE_INCREASES/DECREASES`, and the four outcome maps.

### `utils/build_config.py` — the resolver
At import time it:
1. Calls `_read_env_file()` to parse `config/build.env` (via `get_path`, so it finds the bundled copy inside a frozen exe). Returns `{}` if the file is absent.
2. Resolves each flag with a **default fallback**:
   ```python
   _build_condition = env.get("BUILD_CONDITION", DEFAULT_BUILD_CONDITION)  # None in dev
   _message_type    = env.get("MESSAGE_TYPE",    DEFAULT_MESSAGE_TYPE)
   if _message_type == "None": _message_type = None    # the .env stores the literal string "None"
   IS_TEST_BUILD    = env.get("TEST_BUILD", "false").lower() == "true"
   ```
3. **Validates** the values against `VALID_CONDITIONS` and `{"MEX1","MEX2",None}`, falling back to defaults if invalid — a corrupt `.env` can never crash the app, only degrade to dev defaults.
4. Exposes `SPANISH` — the **only** language switch, hand-set in this file (`True` = Spanish).

> **Why the string `"None"` special-case?** The build scripts write `MESSAGE_TYPE=None` as text into `build.env`. Without the `if _message_type == "None": _message_type = None` line, the app would treat the *string* `"None"` as a message type and try to load `mexNone.png`. This one line bridges the text-file world and the Python-`None` world.

The two situations `build_config` must handle:
- **Frozen build:** `build.env` **is** bundled → the scripts' chosen condition/message/test flag are read back.
- **Dev / from source:** no `build.env` exists → everything falls to defaults (`BUILD_CONDITION=None` → manual prompt).

---

## 4. Path resolution — `utils/file_manager.py`

PyInstaller `--onefile` builds unpack into a **temporary** directory (`sys._MEIPASS`) that is deleted on exit. That single fact forces **two** different path helpers:

| Helper | Use for | Dev root | Frozen root |
|---|---|---|---|
| `get_path(*p)` | **Read-only bundled assets** (images, sounds, QSS, `build.env`, `redeem_codes.json`) | project root | `sys._MEIPASS` (temp unpack dir) |
| `get_writable_path(*p)` | **Files that must persist** (the metrics CSVs, `user_data.json`) | project root | `os.path.dirname(sys.executable)` (next to the `.exe`) |

> **Why two functions?** If metrics were written under `get_path` (i.e. into `_MEIPASS`), they'd be **deleted the moment the app closes** — the researcher would lose all data. `get_writable_path` deliberately targets the folder *beside* the executable so CSVs survive. Conversely, assets must be read from `_MEIPASS` because that's where PyInstaller extracted them. Getting these two backwards is the classic "works in dev, silently loses data in the build" bug — hence the explicit split.

`file_manager` also provides `load_json` / `save_json` (safe, directory-creating JSON helpers) used by the redeem subsystem.

---

## 5. The researcher authority — `core/remote_researcher.py`

`RemoteResearcher` is the **sole authorized owner** of two responsibilities. Nothing else in the app may perform them:

1. **Setting the condition** — `set_condition(x)`:
   - Accepts either a key (`"W"`) or a full name (`"WIN"`), normalizes via `VALID_CONDITIONS`, stores `_current_condition`, and — crucially — calls `update_condition()` in `slot_logic` (the *only* authorized call to it). This is what actually tells the reward engine which DURING map to use.
2. **Enabling metrics** — `start_metrics()`:
   - Calls `log_session_start()` then `enable_metrics(condition)` on the logger, producing the ordered CSV prologue `SESSION_START → START_METRICS`.

**`set_input_data()`** is the interactive dev entry point. It:
- Prompts on the terminal.
- Recognizes the `TEST <CONDITION>` prefix → sets `_test_mode = True` and the condition, then waits for ENTER.
- Otherwise validates a plain condition and recurses on invalid input (re-prompts until valid).

There are also **remote stubs** (`remote_change_condition`, `remote_charge_coin`, `remote_send_message`) that log `MEX` events — placeholders for a future TCP researcher console. They are wired to the logger but never triggered in the current local-input build.

> **Why funnel condition-setting through one method?** Because `set_condition` has a *side effect* (`update_condition` mutates a global in `slot_logic`). If `MainWindow` could set the condition directly, the GUI's idea of the condition and the reward engine's global could drift apart — producing a session whose CSV says "WIN" but whose payouts follow "EQUAL". Centralizing guarantees they move together.

---

## 6. The reward engine — `core/slot_logic.py`

This module is the **single source of truth** for every outcome. It has **no GUI awareness** — it takes numbers in and returns `(reward, multiplier)` out, which makes it fully unit-testable and identical between real play and TEST mode.

### 6.1 Module-global state
```python
initial_budget_before = initial_budget_during = initial_budget_after = None
condition = "EQUAL"
```
- The three `initial_budget_*` capture each phase's *starting* budget, set **lazily** on the first bet of the phase (the `None` guard). In normal play they never need resetting; TEST mode resets them explicitly between sessions.
- `condition` is a plain module global mutated *only* by `update_condition()` (called only by `RemoteResearcher`).

### 6.2 `calculate_reward(budget_before_spin, current_bet_counter, current_bet)` — the dispatcher
The single entry point the GUI calls. It:
1. Determines the phase by testing membership in `PHASES["PHASE_BEFORE"|"PHASE_DURING"|"PHASE_AFTER"]` (global bet numbers 1–20 / 21–40 / 41–60).
2. Lazily sets that phase's `initial_budget_*`.
3. Looks up win/loss in the phase's outcome map.
4. On a **loss** → returns `(0, None)`. On a **win** → dispatches to the right reward function:

| Phase | Win handler |
|---|---|
| BEFORE | `loss_recover(initial_budget_before, …)` |
| AFTER  | `loss_recover(initial_budget_after, …)` — map indexed `BEFORE_AFTER_PHASE[counter - 40]` |
| DURING + EQUAL | `loss_recover(initial_budget_during, …)` |
| DURING + WIN   | `win_increase(…)` |
| DURING + LOSE  | `lose_increase(…)` |
| DURING + other | `raise ValueError` (defensive — an unknown condition is a bug, not a silent skip) |

### 6.3 `loss_recover()` — recover cumulative losses + bet
```python
difference      = max(0, initial_budget_phase - budget_before_spin)   # clamp ≥ 0
expected_reward = round(difference + current_bet, 2)
multiplier      = calculate_multiplier(expected_reward, current_bet)
reward          = round(current_bet * multiplier, 2)
```
The clamp guards the case where the player is already *ahead* of the phase's start (difference would be negative) — the reward then degrades to just the bet back.

### 6.4 `win_increase()` — scripted percentage gains (DURING-WIN)
```python
pct             = EXPECTED_PERCENTAGE_INCREASES.get(current_bet_counter, 0)  # 0 if not a checkpoint
expected_reward = round(pct * initial_budget_during + current_bet, 2)
```
Because it uses `.get(..., 0)`, a winning bet with no percentage entry produces `expected_reward == current_bet` → multiplier 1 (a minimal but non-zero win, keeping the reels "winning").

### 6.5 `lose_increase()` — consolation checkpoints (DURING-LOSE)
Fires only at bets 25, 30, 35 (the wins in `DURING_PHASE_LOSE`):
```python
lose_value          = round(initial_budget_during - budget_before_spin, 2)
expected_lose_value = round(EXPECTED_PERCENTAGE_DECREASES[counter] * initial_budget_during, 2)
lose_difference     = lose_value - expected_lose_value
```
- `lose_difference > 0` (lost *more* than the scripted threshold) → consolation win, `multiplier = calculate_multiplier(lose_difference, bet)`.
- `lose_difference ≤ 0` → `multiplier = 1`.
If the counter is somehow not in `EXPECTED_PERCENTAGE_DECREASES`, it **raises** — again, defensive by design.

### 6.6 `calculate_multiplier()` — snap to the reward table
```python
ideal = round(expected_reward / current_bet, 0)
if ideal in REWARD_TABLE_MUL:      multiplier = ideal
else:                              multiplier = max([m for m in REWARD_TABLE_MUL if m <= ideal],
                                                    default=min(REWARD_TABLE_MUL))
```
Snap-down to the nearest available multiplier; if `ideal` is between 0 and 1, `max(...)` has no candidates and `default=min(table)` (= `1×`) kicks in. This is why the reels can only ever show one of the 18 catalogued multipliers.

### 6.7 `spin_reels(reward, multiplier)` — symbols from the outcome
Purely cosmetic translation of an already-decided outcome:
- `reward == 0` → `random.sample(SYMBOLS, 3)` (three distinct symbols → visibly a loss).
- `reward > 0` → look up `(symbol, occurrence)` in `REWARD_TABLE_MUL[multiplier]`:
  - `occurrence == 3` → `(symbol, symbol, symbol)`.
  - `occurrence == 2` → symbol at two random positions, a different random symbol at the third.
- A win with `multiplier is None` **raises** (would indicate a logic error upstream).

> **Insight — the reels never decide anything.** By the time `spin_reels` runs, the reward is already computed. The symbols are a *rendering* of the result, which is exactly why the 4-second animation can be skipped entirely in TEST mode without changing a single payout.

---

## 7. Metrics & CSV — `core/metrics_logger.py`

### 7.1 Filename resolution — `_build_metrics_csv_path()`
Builds `data/metrics_{CONDITION}_{MESSAGE}_{INDEX}.csv`:
- `{CONDITION}` = `BUILD_CONDITION` or `"MANUAL"` when `None` (dev runs).
- `{MESSAGE}` = `MESSAGE_TYPE` or `"NO_MEX"` when `None`.
- `{INDEX}` = scans the data dir for existing files with the same prefix, takes `max(existing_index) + 1` → **auto-increment per participant**, so no run ever overwrites another.

### 7.2 Construction — `__init__`
- Stores `is_test_build`.
- Computes the CSV path (unless one was injected).
- **If `is_test_build` is False:** creates `data/`, and if the file doesn't exist, writes the header row.
- **If `is_test_build` is True:** does **nothing** — no directory, no file. (Layer 1 of the triple guard.)

### 7.3 The append-only writer
- `_log(event_type, …)` assembles a row: a millisecond-precision timestamp plus optional fields, each formatted to 2 decimals or left blank if `None`.
- `_write_row()` opens the file in append mode (`"a"`) and writes one CSV row. Append-only means a **new session continues the same file** after the previous `SESSION_END`.

### 7.4 The TEST-build triple guard
Three independent layers ensure a TEST build produces **zero** metrics:
1. **No file created** in `__init__` (shown above).
2. **Session logs gated:** `log_session_start()` / `log_session_end()` early-return if `not _metrics_enabled` **and** if `_is_test_build`.
3. **`_metrics_enabled` never becomes True:** because `main.py` skips `start_metrics()` (which is what calls `enable_metrics`) whenever `IS_TEST_BUILD`.

Even `log_bet()` early-returns when `not _metrics_enabled`, so the guard is belt-and-suspenders.

### 7.5 Event API
`enable_metrics(cond)` (→ `START_METRICS`, sets `_metrics_enabled=True`), `log_session_start/end`, `log_bet(bet_number, bet, result_gain, current_coin)` (→ `BET`, no condition arg), and the remote stubs (`log_remote_message`/`_change_condition`/`_charge_coin`, all emitting `MEX`).

---

## 8. The GUI & session loop — `gui/main_window.py`

`MainWindow(QWidget)` is the largest module. It owns the session state and the visible controls.

### 8.1 Constructor highlights
- **Title/watermark** switch on `SPANISH` and `IS_TEST_BUILD` (`"THIS IS A TEST"` / `"ESTO ES UNA PRUEBA"` vs `"Slot Machine"`).
- **Session bounds:**
  ```python
  if IS_TEST_BUILD:  self.bet_counter, self._session_end = 10, 15   # 5 bets: 11..15
  else:              self.bet_counter, self._session_end = 0,  TOTAL_SESSION_BETS
  ```
- Loads the 9 symbol pixmaps via `get_path`.
- Builds the 3-row layout, spin timer (`spin_speed=80 ms`, `roll_frames=50`), starts BGM.

### 8.2 The real spin pipeline (interactive)
```
on_spin()                          # click
  ├─ bet_counter += 1
  ├─ play click.wav, disable spin button
  ├─ validate bet (≤ coins, > 0)
  ├─ budget_before_spin = coins
  ├─ coins -= current_bet          # deduct immediately (real-time feedback)
  ├─ (reward, mult) = calculate_reward(budget_before_spin, bet_counter, current_bet)
  ├─ final_result   = spin_reels(reward, mult)
  └─ spin_timer.start(80ms)        # begin 50-frame animation
animate_spin()  ×50                # every 80 ms: random symbols (cosmetic)
  └─ on final frame: stop timer, release _spinning lock → show_final_result()
show_final_result()
  ├─ paint the settled symbols
  ├─ coins += reward               # apply payout
  ├─ update coin label, validate_bet()
  ├─ result_gain = reward if reward>0 else -current_bet
  ├─ self._metrics.log_bet(...)    # ← THE CSV WRITE HAPPENS HERE (end of animation)
  ├─ watermark "You won +X" / "Try again"
  ├─ if bet_counter == 40 → arm message/survey (rewire spin button)
  └─ if bet_counter ≥ _session_end → disable button, QTimer.singleShot(3000, close)
```

> **Timing consequence:** the `BET` row is logged at the **end** of the animation. Force-closing mid-animation loses that bet (only `SESSION_END` gets written by `closeEvent`). This is documented behaviour, not a bug — but worth knowing when auditing a short CSV.

### 8.3 Bet controls
`increase_bet`/`decrease_bet` step by `BET_STEP` within `[0, MAX_BET]`; `on_bet_manual_input` parses typed text (comma→dot, clamp, snap to 0.10); `validate_bet` enables SPIN only when `0 < bet ≤ coins and not _spinning`.

### 8.4 The message + survey handoff (bet 40)
At bet 40, `show_final_result` **rewires** the SPIN button:
- If `MESSAGE_TYPE` is set → button → `on_message()` (opens `MessageWindow`).
- If `MESSAGE_TYPE is None` → button → `open_survey_window()` directly.

`open_message_callback` (fired when the overlay closes) → `open_survey_window()`:
- Locks all controls (`_lock_game_window`), stops music.
- Shows a 5 s "get ready" watermark, then `_open_survey_browser()` opens the **Qualtrics** URL in a new browser tab.
- Rewires SPIN back to `on_spin`, and schedules `_unlock_game_window` after 35 s so the participant finishes the survey before resuming into bet 41.

### 8.5 `closeEvent` — clean shutdown
Logs `SESSION_END`, calls `super().closeEvent`, then `sys.exit()`. The explicit `sys.exit()` exists because **Alt+F4 only closes the window**, leaving the process (and music) alive otherwise — a real bug they hit and fixed here. (A commented "IMOTIONS forced" variant using `os._exit(0)` is preserved for environments where PyQt swallows `sys.exit`.)

### 8.6 TEST-mode driver (developer)
`_execute_spin_logic()` is a **synchronous** mirror of `on_spin`+`show_final_result` with **no** animation and **no** game logic of its own — it runs the exact same `calculate_reward → spin_reels → log_bet` pipeline instantly. `testing_statistics_v1/v2` drive it in a loop (see §13).

---

## 9. The message overlay — `gui/message_window.py`

`MessageWindow(QWidget)` is a **child widget of MainWindow** (not a separate OS window), sized to cover the client area (`setGeometry(0,0,parent.width(),parent.height())`) while leaving the title bar free — so the participant can still move/resize/close the main window.

- Loads `mex1.png` (MEX1) or `mex2.png` (MEX2), falling back to `banana.png` if missing.
- **MEX1:** CLOSE enabled immediately (`_timer_done = True`).
- **MEX2:** CLOSE disabled; a 1-second `QTimer` counts down `MESSAGE_TIMER` (180 s), updating `countdown_label`; on expiry it enables CLOSE and turns it green.
- **Programmatic close is blocked** before the timer expires (`closeEvent` calls `event.ignore()`), preventing the participant from skipping the coercive condition.
- `open_message_callback` is fired **exactly once** (guarded by `_callback_fired`) when the overlay closes.
- Image rescales responsively (`_render_image` on `showEvent`/resize, reserving space for the bottom CLOSE+countdown bar); `MainWindow.resizeEvent` calls `_sync_to_parent` to keep the overlay aligned.

---

## 10. Redeem subsystem — `redeem_logic.py` + `redeem_dialog.py`

- **`RedeemDialog`** (`QDialog`): a text field + "Redeem" button; on submit it calls back into `MainWindow.redeem_code_callback`, showing a success/failure `QMessageBox`.
- **`validate_redeem_code(code)`**: uppercases/trims the code, loads valid codes from `data/redeem_codes.json`, checks it isn't already in `user_data.json`'s `used_redeem_codes`, and on success **persists** the code as used (via `save_json`) before returning its coin value. Returns `0` for unknown/empty/already-used codes.
- `MainWindow.redeem_code_callback` adds the awarded coins, refreshes the label, and re-validates the bet.

> Codes are **one-time** by construction: the "used" list is written to disk, so a code survives across sessions and can never be redeemed twice.

---

## 11. Audio — `core/sound_manager.py`

A thin wrapper over `pygame.mixer` (initialized at import). `play_bgm(file, loop=True)` loops `bgm.mp3`; `stop_bgm()` halts it (used when a message/survey is active); `play_sfx(file)` plays one-shots (`click.wav`, `spin.wav`, `win.wav`). All paths go through `get_path("gui","assets",...)` so they resolve in both dev and frozen builds. Missing files degrade gracefully (printed warning, no crash).

---

## 12. The build system in depth

This is the part with the most moving pieces. The core problem: **PyInstaller freezes Python source into a standalone `.exe`, but the app needs to know *at runtime* which condition/message/test-mode it was built for.** The solution is a **temporary env file baked into the bundle.**

### 12.1 The `build.env` mechanism (the heart of it)

```
build script                     PyInstaller                     frozen app at runtime
────────────                     ───────────                     ─────────────────────
1. write config/build.env   ──►  2. --add-data bundles it   ──►  3. build_config.py reads it
   BUILD_CONDITION=W              into the exe as config/         via get_path(...) → _MEIPASS
   MESSAGE_TYPE=MEX1                                              → BUILD_CONDITION="W", etc.
4. finally: delete build.env
   (dev state restored)
```

- The build script **writes** `config/build.env` with the chosen flags.
- PyInstaller's `--add-data "{BUILD_ENV};config"` **copies it into the bundle** under `config/`.
- At runtime, `build_config._read_env_file()` finds it via `get_path("config","build.env")` (which resolves to `_MEIPASS/config/build.env` in the frozen exe) and reads the flags back.
- The build script's `finally:` block **deletes** `build.env` afterwards so the dev tree returns to "no env → manual mode".

> **Why write-then-delete instead of keeping the file?** Because the checked-in dev state must be "manual mode" (`BUILD_CONDITION=None`). The env file exists only transiently, purely to smuggle config *into* the bundle. After the build, it's garbage — hence the `finally` cleanup. This is why running `python main.py` from source always prompts, even right after building.

### 12.2 `build/build_all.py` — the 6 production builds

Iterates `BUILDS = [("W","MEX1"), ("W","MEX2"), ("W",None), ("L","MEX1"), ("L","MEX2"), ("L",None)]` (the three `("E",…)` entries are commented out — EQUAL was dropped from the study). For each `(condition, mex)`:
1. Writes `build.env` with `BUILD_CONDITION=<c>` and `MESSAGE_TYPE=<mex>`.
2. Computes `name = SlotMachine_{c}_{mex|NO_MEX}`.
3. Runs PyInstaller with:
   - `--onefile --windowed` (single exe, no console),
   - `--name`, `--distpath dist/`, `--workpath build/pyinstaller_work/`, `--specpath build/`,
   - `--add-data` for `gui/assets`, `gui/styles`, `data/redeem_codes.json`, **and `build.env → config`**,
   - `--collect-all pygame` (PyInstaller doesn't auto-bundle pygame's data),
   - entry point `main.py`.
   - `check=True` so a failed build **aborts loudly** rather than producing a broken exe.
4. `finally:` deletes `build.env`.

**Output:** `dist/SlotMachine_{W|L}_{MEX1|MEX2|NO_MEX}.exe` (6 files).

### 12.3 `build/build_test.py` — the single TEST build

Same PyInstaller invocation, but the `build.env` it writes is:
```
BUILD_CONDITION=E     # must be present or the app drops to manual mode; value is irrelevant here
TEST_BUILD=true       # → IS_TEST_BUILD, drives 5-bet session + zero metrics + "THIS IS A TEST"
```
It does **not** bundle `redeem_codes.json` (the test build is stripped down). **Output:** `dist/SlotMachine_TEST.exe`.

### 12.4 The launcher problem & `build/build_all_launchers.py`

**Why launchers exist:** iMotions can only fire a stimulus by an **`.exe` path**, and after the stimulus it needs a keystroke to advance to the next survey page. A launcher wraps the game exe to provide exactly that.

`build_all_launchers.py` holds two string templates:

- **`BAT_TEMPLATE`** — a `.bat` that `cd`s to its own folder, `start /wait`s the target exe (blocks until it exits), waits 1 s, then uses PowerShell `SendKeys` to send `+{PGDN}` (Shift+PageDown) to iMotions.
- **`LAUNCHER_TEMPLATE`** — the Python equivalent. Its runtime logic:
  ```python
  if getattr(sys,'frozen',False):  exe_dir = Path(sys.executable).parent   # next to the launcher exe
  else:                            exe_dir = Path(__file__).parent/"dist"  # dev
  TARGET_EXE = exe_dir / "{EXE_NAME}.exe"
  subprocess.run([str(TARGET_EXE)])          # blocks until the game exits
  time.sleep(1); send_shift_pagedown()       # advance iMotions
  # on any error → write launcher_error.log next to the launcher
  ```
  The `{EXE_NAME}` placeholder is `.replace()`d with the concrete target name.

For each of the 6 production builds the script:
1. Writes `dist/bat_launcher_{c}_{mex}.bat` from `BAT_TEMPLATE`.
2. Writes a **temporary** `_temp_launcher_{c}_{mex}.py` from `LAUNCHER_TEMPLATE`.
3. PyInstaller-builds it (`--onefile --windowed --name=launcher_{c}_{mex}`) into `dist/`.
4. `finally:` deletes the temp `.py`.

**Output:** 6 × `launcher_{c}_{mex}.exe` (ready for iMotions) + 6 × `bat_launcher_{c}_{mex}.bat` (backup; must be run through a Bat-to-Exe converter before iMotions can use them).

> **Two paths, same behaviour.** The `.exe` launcher (Path A) is self-contained and preferred. The `.bat` (Path B) is a fallback that requires an external Bat-to-Exe conversion because iMotions won't accept `.bat` paths. Both send the identical Shift+PageDown.

### 12.5 `build/build_imotions_launcher.py` — the TEST launcher

Builds the **standalone** [imotions_launcher.py](imotions_launcher.py) (whose body is byte-for-byte the `LAUNCHER_TEMPLATE`, but hardcoded to `TARGET_EXE = SlotMachine_TEST.exe`) into `dist/imotions_launcher.exe`. This is the iMotions launcher for the familiarization TEST build.

> A simpler root-level [app_launcher.py](app_launcher.py) also runs `SlotMachine_TEST.exe` but **omits** the Shift+PageDown — it's a bare backup, *not* the iMotions launcher.

### 12.6 Full build → deploy pipeline

```
① set SPANISH in utils/build_config.py            (True=ES / False=EN)
② python build/build_all.py           → dist/SlotMachine_{W|L}_{MEX1|MEX2|NO_MEX}.exe   (×6)
③ python build/build_test.py          → dist/SlotMachine_TEST.exe
④ python build/build_all_launchers.py → dist/launcher_*.exe (×6) + dist/bat_launcher_*.bat (×6)
⑤ python build/build_imotions_launcher.py → dist/imotions_launcher.exe
⑥ (Path B only) convert each .bat with a Bat-to-Exe tool
⑦ place each SlotMachine_X_Y.exe in the SAME folder as its launcher   (LAUNCHERS/X_Y/)
⑧ register the launcher .exe as the iMotions stimulus
```
Repeat ①–⑤ once per language, keeping the ES/EN outputs in separate folders. Full operational detail lives in [INSTRUCTIONS.md](INSTRUCTIONS.md).

> **Artifacts note:** `*.spec`, `build/pyinstaller_work/`, and `dist/` are all git-ignored — every build regenerates them.

---

## 13. Test mode internals

Two loops, both driving `_execute_spin_logic()`:

- **`testing_statistics_v1()`** — resets session state + phase budgets, runs **one** 60-bet session with random bets, and `_execute_spin_logic`'s (currently commented) auto-close would end it.
- **`testing_statistics_v2()`** *(the active one)* — loops `TOTAL_TESTS` (50) sessions. For each session after the first it picks a **random** condition (`random.choice` of WIN/EQUAL/LOSE), calls `remote_researcher.set_condition` + `start_metrics` (re-arming logging), resets phase budgets, and runs 60 random-bet spins. After all 50 it calls `self.close()` → `SESSION_END`. Net: **3000 logged spins** appended to one CSV — a statistical stress test that the reward engine never produces impossible values.

Both reset `slot_logic.initial_budget_{before,during,after} = None` before each session (imported as `_sl`) — without this, a second session would inherit the previous session's phase-start budgets and compute wrong recoveries.

---

## 14. Critical invariants recap

| # | Invariant | Enforced by |
|---|---|---|
| 1 | Exactly 60 bets per production session (5 for TEST) | `_session_end`, auto-close in `show_final_result` |
| 2 | Every outcome is pre-scripted; luck is an illusion | deterministic maps in `constants.py` + `slot_logic` |
| 3 | Condition set in exactly one place | `RemoteResearcher.set_condition` → `update_condition` |
| 4 | Metrics enabled in exactly one place | `RemoteResearcher.start_metrics` → `enable_metrics` |
| 5 | `bet_counter` incremented in exactly one place per path | `on_spin` (real) / `_execute_spin_logic` (test) |
| 6 | All reward/symbol logic in one module | `core/slot_logic.py` |
| 7 | TEST build writes zero metrics | triple guard in `metrics_logger` + skipped `start_metrics` |
| 8 | Assets read from bundle, data written beside exe | `get_path` vs `get_writable_path` |
| 9 | Build config travels via a transient bundled `build.env` | build scripts write→bundle→delete; `build_config` reads |

**Break any of rows 3–6 and you get the same class of bug:** a session whose recorded data no longer matches the outcomes the player actually experienced. That is the failure mode the entire single-source architecture exists to prevent.
