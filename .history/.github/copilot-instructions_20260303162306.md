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
MAX_BET = 2.0      # user input > 2.0 is capped to 2.0 automatically
BET_STEP = 0.10    # 20 increments from MIN_BET to MAX_BET
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

### Phase-global budget variables (in `core/slot_logic.py`)

Three globals track each phase's starting budget. Each is initialized to `None` and set **once** on the first bet of that phase:

```python
initial_budget_before = None  # set to INITIAL_BUDGET on bet 1
initial_budget_during = None  # set to budget_before_spin on bet 21
initial_budget_after  = None  # set to budget_before_spin on bet 41
```

The `None` guard inside `calculate_reward` ensures no external reset function is needed. For multi-session TEST runs, reset all three to `None` at the start of `testing_statistics()`.

## Spin Execution Flow (per bet)

When the user presses SPIN (or `_execute_spin_logic` runs in TEST mode):

1. Increment `bet_counter`.
2. Save `budget_before_spin` (coins **before** deduction).
3. Deduct bet: `coins -= current_bet`.
4. Call `calculate_reward(budget_before_spin, bet_counter, current_bet)` → returns `(reward, multiplier)`.
5. Call `spin_reels(reward, multiplier)` → returns `(r1, r2, r3)`.
6. Apply reward: `coins += reward`.
7. Log via `metrics_logger.log_bet(...)`.
8. Auto-close if `bet_counter >= TOTAL_SESSION_BETS`.

## Reward Logic (all in `core/slot_logic.py`)

### `calculate_reward(budget_before_spin, current_bet_counter, current_bet) → (reward, multiplier)`

Returns `(0, None)` on loss. On win, returns `(reward, multiplier)` using the logic below.

---

### BEFORE / AFTER / DURING-EQUAL — loss recovery

```
EXPECTED_REWARD = initial_budget_phase - budget_before_spin + current_bet
```

- `budget_before_spin` = coins **before** the bet is deducted this spin.
- `initial_budget_phase` = 100 for BEFORE; `budget_before_spin` at bet 21 for DURING; `budget_before_spin` at bet 41 for AFTER.
- Recovers all cumulative losses since the phase started, plus the current bet.

**Example:** after 3 losses totalling 2.00, 4th bet = 0.80 → `EXPECTED_REWARD = 2.00 + 0.80 = 2.80`.

Then apply **Multiplier Calculation** (section below) to get the final `reward`.

---

### DURING-WIN reward

```
EXPECTED_REWARD = EXPECTED_PERCENTAGE_INCREASES[bet_number] × initial_budget_during + current_bet
```

- `EXPECTED_PERCENTAGE_INCREASES` keys on bet number (21–40), values are decimal fractions (e.g. `0.05` = 5%).
- **Example:** budget_during = 100.2, pct = 5%, bet = 1.5 → `0.05 × 100.2 + 1.5 = 6.51`.

Then apply Multiplier Calculation.

---

### DURING-LOSE reward (consolation wins only)

Compute:
```
LOSE_VALUE          = initial_budget_during - budget_before_spin + current_bet
EXPECTED_LOSE_VALUE = EXPECTED_PERCENTAGE_DECREASES[bet_number] × initial_budget_during + current_bet
DIFFERENCE         = LOSE_VALUE - EXPECTED_LOSE_VALUE
```

| Case | Condition | Action |
|---|---|---|
| Player lost **too much** | `DIFFERENCE > 0` | `IDEAL_MULTIPLIER = round(DIFFERENCE / current_bet)`, then resolve REAL_MULTIPLIER |
| Player did **not lose enough** | `DIFFERENCE ≤ 0` | `multiplier = 1` |

Final: `reward = current_bet × multiplier`.

**Example:** actual loss = 5.40, expected loss = 4.995 → difference = 0.405 → consolation = 0.405.

---

### Multiplier Calculation (shared)

```
IDEAL_MULTIPLIER = round(EXPECTED_REWARD / current_bet)   # 0 decimal places
```

1. If `IDEAL_MULTIPLIER` exists in `REWARD_TABLE_MUL` → use it.
2. Else → use the nearest **lower** key in the table.
3. If no lower key exists → use the nearest **higher** key.

```
REWARD = current_bet × SELECTED_MULTIPLIER
```

The bet has already been deducted before `reward` is added back.

## Symbol Selection Logic (`spin_reels` in `core/slot_logic.py`)

Signature: `spin_reels(reward, multiplier) → (r1, r2, r3)`

Called **after** `calculate_reward`. Steps:

1. If `reward == 0` (loss) → return 3 distinct random symbols from `SYMBOLS`.
2. Look up `multiplier` in `REWARD_TABLE_MUL` → get `(symbol, occurrences)`.
3. Build the 3-reel tuple:
   - `occurrences == 3` → `(symbol, symbol, symbol)`
   - `occurrences == 2` → matching symbol at two random positions, a different symbol at the third.

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
- `log_bet(bet_number, bet, result_gain, current_coin)` — no `condition` arg; the CONDITION column is not logged on BET rows.
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
