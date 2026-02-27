# Slot Machine – Workspace Instructions

## Architecture

```
main.py                  # Entry point: creates MetricsLogger, RemoteResearcher, MainWindow
core/
  slot_logic.py          # ALL game logic: phase maps, reward calc, symbol selection
  metrics_logger.py      # Append-only CSV logger (data/metrics.csv)
  remote_researcher.py   # Sole authority for session condition; controls test_mode
  sound_manager.py       # Audio helpers (pygame.mixer)
  redeem_logic.py        # Redeem-code validation
gui/
  main_window.py         # PyQt5 UI + session flow (bet_counter, phase tracking)
  redeem_dialog.py       # Redeem code dialog
utils/
  file_manager.py        # Path resolution helper (get_path)
data/
  metrics.csv            # Append-only session log (auto-created)
```

## Experimental Protocol

- **60 bets per session**, auto-close after bet 60.
- Three phases of 20 bets each, determined by `bet_counter`:
  - `PHASE_BEFORE` bets 1–20
  - `PHASE_DURING` bets 21–40
  - `PHASE_AFTER` bets 41–60
- Condition (`E`/`W`/`L`) affects **only** `PHASE_DURING`. BEFORE and AFTER are identical across all conditions.
- `INITIAL_BUDGET = 100`, `MIN_BET = 0.1`, `MAX_BET = 2.0`, `BET_STEP = 0.1`.

## Session Constants (defined in `gui/main_window.py`)

```python
INITIAL_BUDGET = 100
MIN_BET = 0.10
MAX_BET = 2.0
BET_STEP = 0.10
TOTAL_SESSION_BETS = 60
PHASE_LENGTH = 20
```

## Deterministic Outcome Maps (defined in `core/slot_logic.py`)

Each map keys on the **global** bet number (1–60) and holds `1` (win) or `0` (loss).

| Map | Used for |
|---|---|
| `BEFORE_AFTER_PHASE` | PHASE_BEFORE (1–20) and PHASE_AFTER (41–60) |
| `DURING_PHASE_EQUAL` | PHASE_DURING with condition EQUAL |
| `DURING_PHASE_WIN` | PHASE_DURING with condition WIN |
| `DURING_PHASE_LOSE` | PHASE_DURING with condition LOSE |

Phase helper: look up outcome with `BEFORE_AFTER_PHASE[bet_number]` (bets 1–20 or 41–60) or the appropriate DURING map using the same bet_number key.

## Reward Logic (all in `core/slot_logic.py`)

### `calculate_reward(initial_budget, budget_before_spin, current_bet) → float`

Used for **BEFORE, AFTER, and DURING-EQUAL** (flat-budget phases):
```
reward = initial_budget - budget_before_spin + current_bet
```
- `budget_before_spin` = coins **before** the bet is deducted this spin.
- `initial_budget` = phase-start budget (100 for BEFORE; budget at end of DURING for AFTER).
- The reward always recovers exactly the cumulative loss since the phase started, plus the current bet.

### DURING-WIN reward
```
reward = EXPECTED_PERCENTAGE_INCREASES[bet_number] × initial_budget_during + current_bet
```
- `EXPECTED_PERCENTAGE_INCREASES` dict keys on bet number (21–40), values are decimal fractions (e.g. 0.05 = 5%).

### DURING-LOSE reward (consolation wins only)
```
lose_value          = initial_budget_during - current_budget + current_bet
expected_lose_value = EXPECTED_PERCENTAGE_DECREASES[bet_number] × initial_budget_during + current_bet
```
- If `expected_lose_value > lose_value` → not enough loss yet → multiplier = 1 (minimum consolation).
- Else → `consolation = lose_value - expected_lose_value`, `multiplier = round(consolation / current_bet)`.

## Symbol Selection Logic (`spin_reels` in `core/slot_logic.py`)

Called **after** the reward is computed. Steps:

1. `ideal_multiplier = round(reward / current_bet)` (0 decimals).
2. Look up `ideal_multiplier` in `REWARD_TABLE_MUL` (keys are valid multipliers).
3. If found → use that `(symbol, occurrences)`.
4. If not found → find closest **lower** valid key; if none exists, use closest **higher**.
5. Build the 3-reel tuple from the selected `(symbol, occurrences)`:
   - occurrences = 3 → `(symbol, symbol, symbol)`
   - occurrences = 2 → matching symbol at two random positions, different symbol at third.
6. On **loss** → return 3 distinct random symbols (no match).

`REWARD_TABLE_MUL` (multiplier → `(symbol, occurrences)`):
```python
{1: ("lemon",2), 2: ("grape",2), 3: ("banana",2), 4: ("cherry",2),
 5: ("diamond",2), 7: ("star",2), 8.5: ("bell",2), 10: ("bar",2), 12: ("seven",2),
 15: ("lemon",3), 20: ("grape",3), 30: ("banana",3), 40: ("cherry",3),
 50: ("diamond",3), 75: ("star",3), 100: ("bell",3), 125: ("bar",3), 150: ("seven",3)}
```

## Critical Single-Source Rules

| Responsibility | Owner |
|---|---|
| Setting session condition | `RemoteResearcher.set_condition()` only |
| Enabling metrics / SESSION_START | `RemoteResearcher.start_metrics()` only |
| Incrementing `bet_counter` | `on_spin()` or `_execute_spin_logic()` only |
| All win/loss/reward/symbol logic | `core/slot_logic.py` only |

**Never** call `update_condition()` or `enable_metrics()` directly from `MainWindow`.

## Metrics CSV Schema

```
TIMESTAMP | EVENT | BET_NUMBER | BET | CONDITION | RESULT | COIN | MESSAGE
```

- Event types: `SESSION_START`, `START_METRICS`, `BET`, `MEX`, `SESSION_END`.
- `log_bet(bet_number, bet, result_gain, current_coin)` — no `condition` arg; condition stored at `enable_metrics` time.
- `result_gain` = `+reward` on win, `-bet` on loss.
- CSV is append-only; new sessions are appended after the previous `SESSION_END`.

## Build & Run

```bash
.\.venv\Scripts\Activate.ps1   # activate venv
python main.py                 # run (prompts for E/W/L or TEST)
python -m py_compile main.py   # syntax check
```

## Code Style

- PyQt5: signals/slots, `QTimer` for animation (80 ms × 50 frames).
- `_execute_spin_logic()` in `main_window.py` is the synchronous spin path used by TEST mode — contains zero game logic.
- Round all monetary values to 2 decimals (`round(..., 2)`).
- All asset paths via `utils.file_manager.get_path(...)`.
