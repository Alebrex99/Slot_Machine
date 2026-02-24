# Slot Machine – Workspace Instructions

## Architecture

```
main.py                  # App entry point: creates MetricsLogger, RemoteResearcher, MainWindow
core/
  slot_logic.py          # Game symbols, reward table, spin logic → BEING REPLACED with deterministic version
  metrics_logger.py      # Append-only CSV logger (data/metrics.csv)
  remote_researcher.py   # Sole authority for session condition; controls test_mode
  sound_manager.py       # Audio helpers (pygame.mixer)
  redeem_logic.py        # Redeem-code validation
gui/
  main_window.py         # PyQt5 UI + session flow (bet counter, phase tracking)
  redeem_dialog.py       # Redeem code dialog
utils/
  file_manager.py        # Path resolution helper (get_path)
data/
  metrics.csv            # Append-only session log (auto-created)
  user_data.json
  redeem_codes.json
```

## Experimental Protocol (key design constraint)

- **60 bets per session**, split into three phases of 20: `PHASE_BEFORE` (1–20), `PHASE_DURING` (21–40), `PHASE_AFTER` (41–60).
- Session condition (`E` / `W` / `L`) controls only `PHASE_DURING` behavior; before/after are identical across conditions.
- `INITIAL_BUDGET = 100`, `MIN_BET = 0.1`, `MAX_BET = 2.0`, `BET_STEP = 0.1`.
- Auto-close on bet 60: `if self.bet_counter >= TOTAL_SESSION_BETS: self.close()`.

## Critical Single-Source Rules

| Responsibility | Owner |
|---|---|
| Setting session condition in `slot_logic` | `RemoteResearcher.set_condition()` only |
| Enabling metrics / logging session start | `RemoteResearcher.start_metrics()` only |
| Incrementing `bet_counter` | `on_spin()` or `_execute_spin_logic()` only |

**Never** call `update_condition()` or `enable_metrics()` directly from `MainWindow`.

## Metrics CSV Schema

```
TIMESTAMP | EVENT | BET_NUMBER | BET | CONDITION | RESULT | COIN | MESSAGE
```

Event types: `SESSION_START`, `START_METRICS`, `BET`, `MEX`, `SESSION_END`.

- `log_bet(bet_number, bet, result_gain, current_coin)` — consolidated, no `condition` arg (condition lives on `_current_condition` set at `enable_metrics` time).
- `result_gain` = `+reward` on win, `-bet` on loss.
- Logger writes always on the GUI thread; no threading.

## Slot Logic Status

`spin_reels()` in `core/slot_logic.py` is a **placeholder** (old probabilistic code kept temporarily).  
`VALID_CONDITIONS` is a dict `{"E":"EQUAL","W":"WIN","L":"LOSE"}`.  
`CONVERTING_TABLE` and expected-value logic have been **removed**.  
Deterministic phase-dependent outcome logic is **TODO** — implement inside `slot_logic.py` only.

## Build & Run

```bash
# activate venv
.\.venv\Scripts\Activate.ps1

# run
python main.py
# prompt asks for condition (E/W/L) or TEST

# syntax check
python -m py_compile main.py
```

No test suite yet. Manual verification via `data/metrics.csv` after a session.

## Code Style

- PyQt5 UI patterns: signals/slots, `QTimer` for animation (80 ms × 50 frames).
- Synchronous spin path `_execute_spin_logic()` exists for automated test runs (avoids `QTimer` delays).
- Round all monetary values to 2 decimals (`round(..., 2)`).
- All paths via `utils.file_manager.get_path(...)`.
