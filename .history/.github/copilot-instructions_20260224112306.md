# Copilot Instructions — Slot Machine

## Architecture

```
main.py                     → entry point: QApplication, RemoteResearcher, MetricsLogger, MainWindow
core/slot_logic.py          → pure game logic: spin_reels(), calculate_reward(), WIN_PERCENTAGE, CONVERTING_TABLE
core/metrics_logger.py      → append-only CSV logger (data/metrics.csv), no game logic
core/remote_researcher.py   → controller of the experiments and application: it has to listen for just one input value = Condition (equal, win, lose) or TEST
core/sound_manager.py       → pygame.mixer wrappers: play_sfx(), play_bgm()
core/redeem_logic.py        → one-time redeem code validation (data/redeem_codes.json)
gui/main_window.py          → QWidget: UI + game flow, receives MetricsLogger via constructor
gui/redeem_dialog.py        → modal QDialog for code redemption
utils/file_manager.py       → get_path(*parts) resolves all paths relative to project root
data/metrics.csv            → append-only; never rewritten, never modified by hand
```

## Critical Architectural Rules

- `update_expected_value()` in `slot_logic.py` must be called **only** by `RemoteResearcher.set_expected_value()`. Never from `metrics_logger.py`, `main_window.py`, or `main.py` directly.
- `MetricsLogger.enable_metrics(expected_value)` only updates the CSV logger's internal state — it does **not** touch `slot_logic`.
- `win_percentage` in `slot_logic.py` is a **decimal fraction** (e.g. `0.244` = 24.4%). Do **not** divide by 100 when comparing with `random.random()`.
- All CSV writes are **append-only** and happen on the GUI thread. No threads, no locks.
- `_execute_spin_logic()` is the only synchronous spin path. `on_spin()` uses QTimer and is asynchronous — never call it inside a loop.

## Code Style

- Python 3.10+, PyQt5, pygame.mixer for audio.
- All paths via `get_path()` — never hardcode absolute paths.
- New UI elements: create widget → set `setObjectName()` → style via `gui/styles/style.qss` when possible; inline `setStyleSheet()` only if QSS causes sizing issues.
- `INITIAL_COINS = 10` constant in `main_window.py` — use it, never hardcode coin values.
- Bet values always rounded to 2 decimal places via `round(x, 2)`.
- Float formatting in CSV and UI: `f"{value:.2f}"`.

## Build and Run

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Run application
python main.py

# TEST MODE: type "TEST" at the first input prompt
# → runs 100 spins × 7 expected values automatically, logs to data/metrics.csv
```

No separate build step. No test framework currently in use.

## Key Data Flows

**Normal spin:**
`on_spin()` → log BET → deduct coins → `spin_reels()` → QTimer animation → `show_final_result()` → `calculate_reward(result, bet)` → log RESULT → update UI

**TEST MODE spin (synchronous):**
`testing_statistics(researcher)` → per expected_value: `researcher.set_expected_value()` → `metrics.enable_metrics()` → 100× `_execute_spin_logic()`

**Session lifecycle:**
`RemoteResearcher.set_input_data()` → `start_metrics()` → `log_session_start()` → `enable_metrics()` → [game runs] → window close → `closeEvent()` → `log_session_end()`

## CSV Schema

`TIMESTAMP | EVENT_TYPE | BET | EXPECTED_VALUE | RESULT | COIN | MESSAGE`

Event types: `SESSION_START`, `SESSION_END`, `START_METRICS`, `BET`, `RESULT`, `MESSAGE`, `CHARGE_COIN`, `CHANGE_EXPECTED_VALUE`

RESULT format: `WIN_3_MATCH_+{reward:.2f}` / `WIN_2_MATCH_+{reward:.2f}` / `LOSS`

## Integration Points

- `RemoteResearcher` stubs (`remote_change_expected_value`, `remote_charge_coin`, `remote_send_message`) are reserved for future remote controlling integration — do not repurpose them.
- `CONVERTING_TABLE` maps `expected_value → win_probability` (decimal). Only keys present in this table are valid expected values.
