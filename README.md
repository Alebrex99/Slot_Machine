## 🎰 Slot Machine — Animated Desktop Slot Machine

**A modern, animated slot machine desktop application built with PyQt5 + Pygame, with fully scripted (deterministic) outcomes and per-session metrics logging.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg">
  <img src="https://img.shields.io/badge/Framework-PyQt5-41cd52.svg">
  <img src="https://img.shields.io/badge/Audio-Pygame.mixer-ffcc00.svg">
  <img src="https://img.shields.io/badge/i18n-ES%20%2F%20EN-orange.svg">
  <img src="https://img.shields.io/badge/License-MIT-green.svg">
  <img src="https://img.shields.io/badge/Status-Active-success.svg">
</p>

> 📚 **Documentation set:**
> - **README.md** *(this file)* — how the application works (conceptual overview).
> - **[INSTRUCTIONS.md](INSTRUCTIONS.md)** — how to run, build, and deploy into iMotions (operational how-to).
> - **[README_DEPTH.md](README_DEPTH.md)** — exhaustive component-by-component technical reference, starting from `main.py`, including the build system in depth.

---

### 🎯 Core Purpose

A desktop slot machine that logs gameplay metrics over **exactly 60 bets** (3 phases of 20). The core invariant is that **the player can never truly win or lose freely — every outcome is scripted in advance** by the selected condition. What looks like luck is a fully deterministic sequence fixed at build/configuration time.

Two conditions are used in production:

| Code | Condition | What the player experiences in bets 21–40 |
|------|-----------|-------------------------------------------|
| **W** | **WIN**  | Budget trends **upward** (16 wins / 4 losses) |
| **L** | **LOSE** | Budget trends **downward** (3 wins / 17 losses) |

> A third condition **E (EQUAL** — flat budget) exists fully in the code but was **not used** in the final production set, so it is commented out of the production build list. It remains available for development and testing.

---

### 🏗️ Architecture (3-Tier System)

```
main.py                     # Entry: MetricsLogger → RemoteResearcher → MainWindow
core/
  slot_logic.py             # ALL game logic (single source of truth)
  constants.py              # Shared constants, outcome maps, reward tables
  metrics_logger.py         # Append-only CSV logger
  remote_researcher.py      # Sole authority for condition + metrics activation
  sound_manager.py          # pygame.mixer audio
  redeem_logic.py           # One-time redeem codes
gui/
  main_window.py            # PyQt5 session loop (bet counter, animations, phases)
  message_window.py         # Full-screen overlay shown at bet 40 (MEX1 / MEX2)
  redeem_dialog.py          # Redeem popup
utils/
  file_manager.py           # get_path() — resolves assets for dev AND frozen builds
  build_config.py           # Reads config/build.env; exposes BUILD_CONDITION, MESSAGE_TYPE, IS_TEST_BUILD, SPANISH
data/
  redeem_codes.json         # Static valid codes
  user_data.json            # Persistent coins + used codes
  metrics_*.csv             # Auto-created, append-only
```

#### 1. Entry Point — [main.py](main.py)
- Builds `MetricsLogger` (prepares the per-run CSV, unless it's a TEST build).
- Builds `RemoteResearcher` — the **only** object allowed to set the condition and enable metrics.
- If `BUILD_CONDITION` is baked in (frozen build) → skips the prompt. Otherwise → interactive terminal prompt.
- Shows `MainWindow`; if TEST mode was requested, runs the automated headless playthrough.

#### 2. Game Logic Core — [core/slot_logic.py](core/slot_logic.py)
The **single source of truth** for all outcomes. Contains the deterministic win/loss maps, the reward-calculation engine, symbol selection, and the per-phase budget bookkeeping. No game logic lives anywhere else.

#### 3. GUI — [gui/main_window.py](gui/main_window.py)
Bet controls, 3 animated reels (50 frames × 80 ms ≈ 4 s per spin), coin display, music toggle, the message/survey system, and the 60-bet session loop.

---

### ⚙️ How a Single Spin Works (Step-by-Step)

The result is **computed the instant SPIN is pressed** — the animation is purely cosmetic and only reveals the already-decided outcome.

1. **User clicks SPIN** → `bet_counter` increments (1 → 60).
2. Snapshot `budget_before_spin` (coins **before** deduction).
3. Deduct the bet: `coins -= current_bet`.
4. **`calculate_reward(budget_before_spin, bet_counter, current_bet)`** → `(reward, multiplier)`.
5. **`spin_reels(reward, multiplier)`** → 3 reel symbols matching the multiplier.
6. Start the 4-second reel animation (`QTimer`, 50 frames of random symbols).
7. **At the end of the animation** (`show_final_result`): `coins += reward`, then **`log_bet(...)`** appends the row to the CSV.
8. At bet 40 → show the message overlay + survey. At bet 60 → auto-close after 3 s.

> ⚠️ **Logging timing:** the BET row is written **at the end of the reel animation**, not on click. If the app is force-closed mid-animation, that bet is never logged (only `SESSION_END` is written by `closeEvent`).

---

### 📊 The 3 Phases

Three phases of 20 bets each, keyed on the **global** bet number (1–60):

| Phase | Bets | Outcome Map | Reward Logic | Condition Effect |
|-------|------|-------------|--------------|------------------|
| **BEFORE** | 1–20  | `BEFORE_AFTER_PHASE` | Recover all cumulative losses + current bet | None (fixed) |
| **DURING** | 21–40 | `DURING_PHASE_{EQUAL\|WIN\|LOSE}` | EQUAL: recovery · WIN: % gains · LOSE: consolation | ✅ **Controls gameplay** |
| **AFTER**  | 41–60 | `BEFORE_AFTER_PHASE` | Recover all cumulative losses + current bet | None (fixed) |

Each map (in [core/constants.py](core/constants.py)) maps a bet number → `True` (win) or `False` (loss). BEFORE and AFTER are **identical and condition-agnostic** — the condition's effect lives entirely in the DURING phase.

**The exact scripted sequences** (✅ = win, ⬜ = loss):

```
BEFORE_AFTER_PHASE (bets 1–20, reused for 41–60):
 1 ⬜  2 ⬜  3 ⬜  4 ✅  5 ⬜  6 ⬜  7 ✅  8 ⬜  9 ⬜ 10 ⬜
11 ⬜ 12 ✅ 13 ⬜ 14 ⬜ 15 ✅ 16 ✅ 17 ⬜ 18 ⬜ 19 ⬜ 20 ✅     → 6 wins / 14 losses (flat)

DURING_PHASE_EQUAL (bets 21–40):   6 wins / 14 losses  → net ≈ 0  (flat)
DURING_PHASE_WIN   (bets 21–40):  16 wins /  4 losses  → strongly upward
DURING_PHASE_LOSE  (bets 21–40):   3 wins / 17 losses  → strongly downward (wins only at 25, 30, 35)
```

> The AFTER phase reuses the BEFORE map via `BEFORE_AFTER_PHASE[bet_number - 40]`, so bet 41 uses index 1, bet 42 uses index 2, and so on — the same "flat" pattern plays out again after the DURING phase.

Per-phase starting budgets are captured once, lazily, at the first bet of each phase (the `None` guard means no external reset is needed in normal play):
```python
initial_budget_before = None   # set to INITIAL_BUDGET (100) on bet 1
initial_budget_during = None   # set to the coins carried in, on bet 21
initial_budget_after  = None   # set to the coins carried in, on bet 41
```

---

### 🧮 How the Multipliers & Percentages Were Designed

The reward system is **fully deterministic**. The win/loss *sequence* is scripted (see the phases above) and, for every scripted win, the payout is *solved* so the running budget reaches a target. **There are no probabilities, no per-spin expected value, and no house-edge/RTP** in the shipped game — a spin's result is fixed before the reels move. These equations were derived in **`File Slot x ale_v2.xlsx`** (three *"Simulazione truccata"* — "rigged simulation" — sheets `_W`/`_U`/`_L`, one per condition) and ported verbatim into [core/slot_logic.py](core/slot_logic.py).

> ⚠️ **Historical note — an earlier, abandoned prototype.** A first exploration (workbook `Slot truccata.xlsx`: sheets *Riflessioni iniziali*, *Simulazione*, and a ~29,500-spin Monte Carlo in *Sheet1*) modelled the machine the *ordinary* way — **probabilistically**, with `P(win)`, symbol/combination probabilities, and a statistical **Expected Value** (e.g. `EV = 0.2·[0.7·7.5 + 0.3·75] = 5.55×`, where each outcome is drawn from a random number vs. a win probability). **That expected-value approach was dropped from the final game** and does *not* describe the shipped logic. Mind the terminology trap: the code's `EXPECTED_REWARD` / `EXPECTED_PERCENTAGE_*` are **deterministic design targets**, not statistical expectations over random spins.

#### Multipliers vs. percentages — different origins

| | Where it comes from | Chosen or derived? |
|---|---|---|
| **Percentages** (`EXPECTED_PERCENTAGE_*`) | set at design time to shape the target curve | **chosen** — design input |
| **Paytable** (`REWARD_TABLE_MUL`) | a fixed slot-style ladder, set once | **chosen** — cosmetic |
| **Multiplier of a spin** | `m = E / bet`, snapped to the paytable | **derived** — per spin |

You never pick a spin's multiplier: you pick the *trajectory* (via the percentages), and each multiplier falls out of the required payout `E`.

#### The target equations (`E` = "how much must this win pay")

```
Recovery  (BEFORE / AFTER / EQUAL) :  E = max(0, B₀ − B) + bet
        └ target = restore the phase anchor B₀ (≈100) → keeps the budget flat

% Gain    (WIN)                    :  E = pct · B_during + bet
        └ target = anchor + a scripted fraction of the DURING start → ratchets upward

Consolation (LOSE)                 :  E = (B_during − B) − pct · B_during
        └ = actual cumulative loss − expected cumulative loss (paid only if > 0)
          → regulates the *rate* of decline instead of reversing it
```
`B₀` = phase-start budget, `B` = current budget, `B_during` = budget entering the DURING phase.

#### Choosing the percentages (the only free parameters)

Recovery needs **no** free numbers (its target is the fixed anchor). WIN/LOSE need one number per scripted win — these *are* `EXPECTED_PERCENTAGE_INCREASES` / `_DECREASES`. They are chosen so the **cumulative** effect over the 20 DURING bets equals the intended total:
```
WIN  :  Σ pct_gain  ≈ total desired growth of the phase   (here ≈ +80% of B_during → ~100 → ~157)
LOSE :  pct_loss[k] = intended cumulative loss by checkpoint k   (5%, 15%, 15% at bets 25/30/35)
```
Large single values (15%) create visible jumps; small ones (0.5%) keep it believable. The **paytable rungs** (`1,2,3,4,5,7,8.5,10,12,15,20,…`) are spaced densely enough that `m = E/bet` almost always lands on/near a real rung, so the snap error stays negligible — and any residual error is absorbed at the next recovery win.

#### The designed trajectories

The three conditions differ **only** in the DURING phase. Budget vs. bet, extracted from the deterministic `_W`/`_U`/`_L` sheets of `File Slot x ale_v2.xlsx` (one 60-bet session each, scripted outcomes + random bets — exactly what the game does):

```
Budget
  175 |               #
  168 |              # ####          WIN   : flat →  +80%  → hold  (100 → 157 → 168)
  161 |             #
  154 |
  146 |
  139 |            #
  132 |
  125 |           #
  118 |         ##
  111 |        #
  104 |*    * #
   96 | ****.****==========          EQUAL : flat throughout       (~100 the whole session)
   89 |          ...
   82 |             .......          LOSE  : flat → −16%  → drift  (100 →  84 →  79)
   75 |
      +--------------------
       bet: 1            20  40  60
       │─── BEFORE ───│ DURING │ AFTER │
       #=WIN   ==EQUAL   .=LOSE
```
The condition's effect is entirely in **DURING (21–40)**: the curves are indistinguishable in BEFORE, fan out sharply through DURING, then each holds its new level in AFTER (because AFTER re-anchors to whatever budget DURING produced).

#### The equations, as ported to code

The spreadsheet columns map **one-to-one** onto the Python functions:

| Purpose | Excel formula (`File Slot x ale_v2.xlsx`) | Python (`slot_logic.py`) |
|---|---|---|
| **Recover losses** (BEFORE / AFTER / EQUAL) | `E = IF($B$2−B > 0, $B$2−B, 0) + C` | `loss_recover()`: `max(0, initial − budget) + bet` |
| **% gain** (WIN) | `E = $B$22 × F + C` | `win_increase()`: `pct × initial_during + bet` |
| **Consolation** (LOSE) | `E = ($B$22 − B) − (F × $B$22)` | `lose_increase()`: `lose_value − expected_lose_value` |
| **Ideal multiplier** | `G = ROUND(E / C, 0)` | `round(expected_reward / bet, 0)` |
| **Snap to paytable** | `H = XLOOKUP(exact → −1 → +1)` | exact key → nearest **lower** → nearest **higher** |
| **Real vs. shown gain** | `J = −C + I×C` · `K = I×C` | real gain `= reward − bet` · reward `= bet × mult` |

*(`$B$2` = the 100-coin start, `$B$22` = the DURING-start budget, `C` = bet, `F` = the chosen percentage, `T`/`U` = the paytable.)*

> **Why deterministic instead of probabilistic?** The abandoned probabilistic prototype could only control outcomes *on average*: across many runs the budget would trend as intended, but any *single* run might hit a wild streak that breaks the intended condition. By scripting the win/loss sequence and solving each win for its exact payout, **every** run follows the intended trajectory. The cost is that the payout must adapt to the player's variable bet, hence `m = E/bet` snapped to the paytable. The `XLOOKUP` fallback chain (exact → smaller → larger) is precisely why `calculate_multiplier()` snaps down first and only falls up as a last resort: it reproduces the spreadsheet's own resolution order.

The three sections below document each ported function in detail.

---

### 💰 Reward Logic

Each **win** is turned into a concrete reward + multiplier by one of three functions in [core/slot_logic.py](core/slot_logic.py). A **loss** always returns `(0, None)` and no reward is applied.

#### 1. `loss_recover()` — BEFORE / AFTER / DURING-EQUAL

Restores every coin lost since the phase began, plus the current bet:
```
difference      = max(0, initial_budget_phase - budget_before_spin)   # clamped ≥ 0
EXPECTED_REWARD = round(difference + current_bet, 2)
```
> ⚠️ The `max(0, …)` clamp matters: if the player is *above* the phase's starting budget (won more than lost so far), `difference` would go negative — the clamp prevents a "negative recovery" and the reward becomes just the bet back (multiplier 1).

**Worked example (BEFORE phase):**
```
initial_budget_before = 100.00 · budget_before_spin = 97.20 · current_bet = 0.80
difference      = 100.00 - 97.20 = 2.80
EXPECTED_REWARD = 2.80 + 0.80 = 3.60
IDEAL_MULTIPLIER = round(3.60 / 0.80) = 4   → 4× exists → cherry pair
reward = 0.80 × 4 = 3.20   (real gain = 3.20 − 0.80 = 2.40)
```

#### 2. `win_increase()` — DURING-WIN

A scripted **percentage gain** relative to the DURING starting budget:
```
pct             = EXPECTED_PERCENTAGE_INCREASES.get(bet_number, 0)   # 0 if not a checkpoint
EXPECTED_REWARD = round(pct × initial_budget_during + current_bet, 2)
```
`EXPECTED_PERCENTAGE_INCREASES` (decimal fractions, keyed on winning bet numbers 21–40):
```
21:2.5% · 23:2.5% · 24:8%  · 26:0.5% · 27:5%  · 29:5%
32:2.5% · 33:5%   · 35:15% · 37:4%   · 38:7.5% · 39:7.5% · 40:15%
```
If a winning bet isn't in the map, `pct = 0` → `EXPECTED_REWARD = current_bet` → multiplier 1 (a minimal win).

**Worked example (DURING-WIN, bet 35):**
```
initial_budget_during = 105.20 · pct(35) = 0.15 · current_bet = 1.50
EXPECTED_REWARD = 0.15 × 105.20 + 1.50 = 17.28
IDEAL_MULTIPLIER = round(17.28 / 1.50) = 12   → 12× exists → seven pair
reward = 1.50 × 12 = 18.00
```

#### 3. `lose_increase()` — DURING-LOSE (consolation only)

Fires only at the three winning checkpoints of `DURING_PHASE_LOSE` (**bets 25, 30, 35**). It gives a small "consolation" prize *only if the player has lost more than the scripted threshold*:
```
LOSE_VALUE          = round(initial_budget_during - budget_before_spin, 2)
EXPECTED_LOSE_VALUE = round(EXPECTED_PERCENTAGE_DECREASES[bet_number] × initial_budget_during, 2)
DIFFERENCE          = LOSE_VALUE - EXPECTED_LOSE_VALUE
```
`EXPECTED_PERCENTAGE_DECREASES = {25: 5%, 30: 15%, 35: 15%}`.
- If `DIFFERENCE > 0` (lost more than expected) → consolation win, `multiplier = calculate_multiplier(DIFFERENCE, bet)`.
- If `DIFFERENCE ≤ 0` (didn't lose enough) → `multiplier = 1` (smallest possible prize).

> Note: unlike the other two functions, `lose_increase` does **not** add the current bet into its target value — the subtraction of expected-vs-actual loss already accounts for it.

#### Multiplier resolution (shared) — `calculate_multiplier()`

```
IDEAL_MULTIPLIER = round(EXPECTED_REWARD / current_bet, 0)
```
- If `IDEAL_MULTIPLIER` is a key in `REWARD_TABLE_MUL` → use it directly.
- Otherwise → use the **nearest lower** key (`max(m for m in table if m ≤ ideal)`).
- If no lower key exists (ideal is between 0 and 1) → fall back to the **minimum** key (`1×`).

The final reward is always `round(current_bet × multiplier, 2)`.

---

### 🎰 Symbol Selection

There are **9 reel symbols** (`SYMBOLS` in [core/constants.py](core/constants.py)):

```
banana · bar · bell · cherry · diamond · grape · lemon · seven · star
```

Once the multiplier is resolved, `spin_reels()` looks it up in the **complete** `REWARD_TABLE_MUL`, which maps every multiplier → `(symbol, occurrences)`. This is the full table (not an excerpt):

| Multiplier | Symbol | Occurrences | Multiplier | Symbol | Occurrences |
|---|---|---|---|---|---|
| **1×**   | lemon   | 2 (pair) | **15×**  | lemon   | 3 (triple) |
| **2×**   | grape   | 2 (pair) | **20×**  | grape   | 3 (triple) |
| **3×**   | banana  | 2 (pair) | **30×**  | banana  | 3 (triple) |
| **4×**   | cherry  | 2 (pair) | **40×**  | cherry  | 3 (triple) |
| **5×**   | diamond | 2 (pair) | **50×**  | diamond | 3 (triple) |
| **7×**   | star    | 2 (pair) | **75×**  | star    | 3 (triple) |
| **8.5×** | bell    | 2 (pair) | **100×** | bell    | 3 (triple) |
| **10×**  | bar     | 2 (pair) | **125×** | bar     | 3 (triple) |
| **12×**  | seven   | 2 (pair) | **150×** | seven   | 3 (triple) — 🎰 jackpot |

Notice the deliberate structure: each of the 9 symbols appears **twice** — once as a lower **pair** multiplier (1×–12×) and once as a higher **triple** multiplier (15×–150×). Triples always pay far more than pairs, and the "richest" symbols (`seven`, `bar`, `bell`) carry the biggest multipliers, so a triple-seven visually reads as the jackpot.

**How the reels are populated ([slot_logic.py](core/slot_logic.py) `spin_reels`):**

| Outcome | Reels produced |
|---|---|
| **Loss** (`reward == 0`) | `random.sample(SYMBOLS, 3)` → three **distinct** random symbols, guaranteed no accidental match |
| **Win, `occurrences == 3`** | `(symbol, symbol, symbol)` → all three reels identical |
| **Win, `occurrences == 2`** | two random reel positions get `symbol`; the third gets a **different** random symbol (`random.choice` from the remaining 8) |

> 🔎 The visual result is purely a *consequence* of the already-computed reward/multiplier — the symbols never determine the payout, they only illustrate it.

---

### 🖼️ The Message + Questionnaire System (bet 40)

At the boundary between the DURING and AFTER phases (bet 40), the app shows a full-screen image overlay, then opens an online questionnaire in the browser. The overlay variant is fixed per build via `MESSAGE_TYPE`:

| `MESSAGE_TYPE` | Overlay shown | Behaviour |
|---|---|---|
| **MEX1** | `mex1.png` | CLOSE button enabled immediately |
| **MEX2** | `mex2.png` | CLOSE locked for a **180 s** countdown (`MESSAGE_TIMER`) |
| **None** (`NO_MEX`) | *(no overlay)* | Goes straight to the questionnaire |

Flow: press SPIN on bet 40 → overlay ([gui/message_window.py](gui/message_window.py)) → on close, the game locks, music stops, and after a 5 s heads-up the **questionnaire URL** opens in the browser. Controls re-enable ~35 s later so the session continues into bets 41–60. Programmatic close of the overlay is blocked until the timer expires.

---

### 🌍 Internationalization

A single flag `SPANISH` in [utils/build_config.py](utils/build_config.py) switches **all** UI text between Spanish (`True`) and English (`False`). It affects window title, watermark, buttons, and every message. Language is chosen at build time, per the `BUILDS/ENG` and `BUILDS/ESP` folders described in INSTRUCTIONS.

---

### 🧪 Testing — two distinct things called "test"

There are **two unrelated testing mechanisms**; don't confuse them:

#### A) The TEST **build** (interface familiarization)
A separate, self-contained executable used to let a user get comfortable with the interface **before** a real session:
- Window title: **"THIS IS A TEST"** / **"ESTO ES UNA PRUEBA"**.
- Session: exactly **5 bets** (`bet_counter` starts at 10, ends at 15 — uses `BEFORE_AFTER_PHASE` indices 11–15).
- **No metrics** — zero CSV files created (triple-layer prevention: no file in `__init__`, session logs guarded by `_metrics_enabled`, `start_metrics()` never called).
- Auto-closes after bet 15. Built via `build/build_test.py`.

#### B) TEST **mode** (headless automated playthrough — for the developer)
Triggered from source by typing `TEST W` / `TEST L` / `TEST E` at the prompt. The GUI stays visible but is driven programmatically via `_execute_spin_logic()` (a synchronous spin with **no** animation and **no** game logic of its own — it mirrors the real pipeline). Two variants exist:

| Method | Behaviour |
|---|---|
| `testing_statistics_v1()` | Runs **1 session** of 60 bets, random bets each spin, then auto-closes. |
| `testing_statistics_v2()` | **(active)** Runs **`TOTAL_TESTS` = 50 sessions × 60 bets = 3000 spins**, re-randomising the condition each session, appending all to one CSV — a statistical stress test of the reward engine. |

Both reset the phase-global budgets before each session so no stale state leaks between runs.

---

### 🎁 Redeem Codes

A small side-system ([core/redeem_logic.py](core/redeem_logic.py) + [gui/redeem_dialog.py](gui/redeem_dialog.py)): one-time codes from `data/redeem_codes.json` add coins to the player's balance; used codes are persisted in `data/user_data.json` so each code works only once. `validate_redeem_code()` uppercases/trims the code, rejects unknown or already-used codes (returns `0`), and on success records the code in `used_redeem_codes` before returning the coin value.

---

### 🕹️ Player-Facing UI & Controls — [gui/main_window.py](gui/main_window.py)

The window is a single `QWidget` with a vertical layout: **top** = bet controls (left) · watermark (center) · redeem + coin balance (right); **middle** = three reels; **bottom** = the SPIN button.

**Bet controls** (bounded by `MIN_BET`/`MAX_BET`/`BET_STEP`):
- `increase_bet()` / `decrease_bet()` — step by `0.10`, clamped to `[0, 2.0]`.
- `on_bet_manual_input()` — typed entry: accepts comma or dot decimals, clamps to `MAX_BET`, and **snaps to the nearest 0.10** (`round(value / BET_STEP) * BET_STEP`).
- `validate_bet()` — the SPIN button is enabled **only** when `0 < bet ≤ coins` **and** no spin is currently animating (`_spinning` lock, prevents double-spins mid-animation).

**Responsive reels:** symbol pixmaps are rescaled from the window size on every `resizeEvent` (via `_update_reels()` / `_compute_reel_size()`), so the reels never clip or drift — replacing an older fixed 400 px approach.

**Audio** — [core/sound_manager.py](core/sound_manager.py) (pygame.mixer):
- `play_bgm("bgm.mp3")` loops background music; `stop_bgm()` halts it (used when a message/survey is active).
- `play_sfx(...)` fires one-shot effects: `click.wav` (buttons), `spin.wav` (spin start), `win.wav` (payout).
- A music toggle button lets the player mute/unmute (`_music_on` flag).

---

### 📋 Data Collection — [core/metrics_logger.py](core/metrics_logger.py)

Append-only CSV, auto-named per run to avoid overwrites:

```
data/metrics_{CONDITION}_{MESSAGE}_{INDEX}.csv
```
- `{CONDITION}` = `W` / `L` / `E`, or **`MANUAL`** when running unbaked from source.
- `{MESSAGE}` = `MEX1` / `MEX2` / **`NO_MEX`**.
- `{INDEX}` auto-increments (`..._1.csv`, `..._2.csv`, …).

**Schema:**
```
TIMESTAMP | EVENT | BET_NUMBER | BET | CONDITION | RESULT | COIN | MESSAGE
```
- `log_bet(bet_number, bet, result_gain, current_coin)` — **no** condition arg; CONDITION is blank on BET rows.
- `result_gain` = `+reward` on a win, `-bet` on a loss.
- **Events:** `SESSION_START` · `START_METRICS` · `BET` · `MEX` · `SESSION_END`.
- Append-only: new sessions follow the previous `SESSION_END` in the same file.
- Only the `START_METRICS` row carries the CONDITION; every column is optional and left blank when not relevant to the event.

**Example rows** (WIN condition):
```
TIMESTAMP,EVENT,BET_NUMBER,BET,CONDITION,RESULT,COIN,MESSAGE
2026-07-24 10:15:02.31,SESSION_START,,,,,,
2026-07-24 10:15:02.31,START_METRICS,,,WIN,,,
2026-07-24 10:15:09.88,BET,1,0.80,,-0.80,99.20,
2026-07-24 10:15:14.02,BET,2,0.80,,-0.80,98.40,
2026-07-24 10:15:19.5,BET,4,1.00,,3.60,102.00,
...
2026-07-24 10:24:41.7,SESSION_END,,,,,,
```
> The `MEX` event and its `MESSAGE` column, plus the remote-charge/remote-condition hooks, are wired in [core/metrics_logger.py](core/metrics_logger.py) as stubs for a future TCP-based remote-control integration; the current build sets everything from local input.

---

### 🔐 Critical Single-Source Rules

| Responsibility | Owner | Note |
|---|---|---|
| Set condition (EQUAL/WIN/LOSE) | `RemoteResearcher.set_condition()` | No direct GUI calls |
| Enable metrics / `SESSION_START` | `RemoteResearcher.start_metrics()` | Gates CSV recording |
| Increment `bet_counter` | `on_spin()` or `_execute_spin_logic()` | Prevents count skips |
| All win/loss/reward/symbol logic | `core/slot_logic.py` | Single source of truth |

**Never** call `update_condition()` or `enable_metrics()` directly from `MainWindow` — doing so corrupts CSV state.

---

### 🔢 Key Constants — [core/constants.py](core/constants.py)

```python
INITIAL_BUDGET = 100.0
MIN_BET, MAX_BET, BET_STEP = 0.10, 2.0, 0.10   # 20 increments
TOTAL_SESSION_BETS = 60
PHASE_LENGTH = 20
MESSAGE_COUNTER_POINT = 40    # overlay shown after this bet
MESSAGE_TIMER = 180           # seconds for the MEX2 countdown
TOTAL_TESTS = 50              # automated stress-test sessions
```

---

### 🎬 Build & Deployment (summary)

| Script | Produces |
|---|---|
| `build/build_all.py` | The **6 production builds** — `SlotMachine_{W\|L}_{MEX1\|MEX2\|NO_MEX}.exe` |
| `build/build_test.py` | The single **TEST build** — `SlotMachine_TEST.exe` |
| `build/build_all_launchers.py` | 6 iMotions launcher `.exe` + 6 backup `.bat` files |
| `build/build_imotions_launcher.py` | The TEST build's iMotions launcher (`imotions_launcher.exe`) |

Each production build is deployed inside iMotions via a **launcher** that runs the slot machine, waits for it to exit, then sends **Shift + Page Down** to advance iMotions to the next item. **Full step-by-step instructions are in [INSTRUCTIONS.md](INSTRUCTIONS.md).**
