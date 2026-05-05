## 🎰 Slot Machine Project - Complete Explanation

**A modern, animated slot machine game built with PyQt5, Pygame, and modular Python architecture.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg">
  <img src="https://img.shields.io/badge/Framework-PyQt5-41cd52.svg">
  <img src="https://img.shields.io/badge/Audio-Pygame.mixer-ffcc00.svg">
  <img src="https://img.shields.io/badge/License-MIT-green.svg">
  <img src="https://img.shields.io/badge/Status-Active-success.svg">
</p>


This is a **research-grade slot machine simulator** built in PyQt5, designed to study human gambling behavior through controlled experimental conditions. Here's the complete breakdown:

---

### **🎯 Core Purpose**
A desktop slot machine game that collects behavioral metrics through **exactly 60 bets** (3 phases of 20 bets each). The researcher controls what players experience via three conditions: **EQUAL** (standard losses recovery), **WIN** (percentage-based gains), or **LOSE** (consolation mechanics during losses).

---

### **🏗️ Architecture (3-Tier System)**

#### **1. Entry Point** (`main.py`)
- Initializes `MetricsLogger` (creates CSV file for data collection)
- Initializes `RemoteResearcher` (asks for condition: E, W, or L)
- Launches GUI window
- Optionally runs auto-test if "TEST" mode selected

#### **2. Game Logic Core** (`core/slot_logic.py`)
Contains **all** game rules:
- **Deterministic outcome maps**: Pre-programmed win/loss sequences for each phase
- **Reward calculation engine**: Computes coin payouts based on phase-specific rules
- **Symbol selection**: Matches 3 reel symbols to the computed multiplier
- **Global phase budgets**: Tracks starting coins for each 20-bet phase

#### **3. GUI Interface** (`gui/main_window.py`)
- Bet controls (up/down buttons, manual input)
- 3 animated reels (spins 50 frames at 80ms each)
- Coin display, spin button, music toggle
- Integrates with `slot_logic.py` for outcomes

---

### **⚙️ How a Single Spin Works (Step-by-Step)**

1. **User clicks SPIN** → `bet_counter` increments (1→60)
2. **Bet deducted** from coins (e.g., 100 - 1.5 = 98.5)
3. **`calculate_reward()`** called with:
   - Budget **before** deduction
   - Current bet number
   - Current bet amount
4. **Outcome determined** by phase-specific map:
   - **BEFORE/AFTER**: Loss recovery (restore all losses + current bet)
   - **DURING-EQUAL**: Loss recovery (like BEFORE)
   - **DURING-WIN**: Percentage gains (5%, 10%, etc.)
   - **DURING-LOSE**: Consolation wins based on over-losses
5. **Multiplier calculated** using `REWARD_TABLE_MUL` (1×, 2×, 5×, 12×, 150×, etc.)
6. **Symbols generated** to match multiplier (e.g., 5× = 2 diamonds + 1 random)
7. **Reward added** to coins
8. **CSV logged** with all metrics
9. **Auto-close** if 60 bets completed

---

### **📊 The 3 Experimental Phases**

| Phase | Bets | Outcome Map | Reward Logic | Condition Effect |
|-------|------|-------------|--------------|------------------|
| **BEFORE** | 1–20 | `BEFORE_AFTER_PHASE` | Recover all losses + bet | None (fixed) |
| **DURING** | 21–40 | Condition-specific | EQUAL: loss recovery<br>WIN: % gains<br>LOSE: consolation | ✅ **Controls gameplay** |
| **AFTER** | 41–60 | `BEFORE_AFTER_PHASE` | Recover all losses + bet | None (fixed) |

---

### **💰 Reward Logic Examples**

#### **BEFORE Phase (or DURING-EQUAL)**
```
Budget starts at 100, losses = 2.50, current bet = 0.80
Expected reward = 2.50 + 0.80 = 3.30
Find nearest multiplier → 3× (matches in REWARD_TABLE)
Actual reward = 0.80 × 3 = 2.40
```

#### **DURING-WIN**
```
Budget at start of DURING = 105.20, percentage increase = 5%, bet = 1.50
Expected reward = (0.05 × 105.20) + 1.50 = 6.76
Find nearest multiplier → 7× 
Actual reward = 1.50 × 7 = 10.50
```

#### **DURING-LOSE (Consolation)**
```
Expected loss = 6.20 (from threshold), actual loss = 7.40
Over-loss = 7.40 - 6.20 = 1.20
Multiplier = 1× → reward = current_bet × 1
(Gives small prize if player lost too much)
```

---

### **🎰 Symbol Selection**

**Reward Table** maps multipliers to symbols:
- `1×` = lemon (2 symbols)
- `5×` = diamond (2 symbols)
- `15×` = lemon (ALL 3 symbols)
- `150×` = seven (ALL 3 symbols) — jackpot!

**When losing** → 3 completely different random symbols (no matching)

---

### **📋 Data Collection** (`metrics_logger.py`)

CSV file saved as: `data/metrics_{CONDITION}_{MESSAGE}_{INDEX}.csv`

**Columns logged:**
```
TIMESTAMP | EVENT | BET_NUMBER | BET | CONDITION | RESULT | COIN | MESSAGE
```

**Event types:**
- `SESSION_START` - Player begins
- `START_METRICS` - Condition activated
- `BET` - Spin result logged (bet, +reward/-loss, final coins)
- `MEX` - Messages from researcher
- `SESSION_END` - Player finishes 60 bets

---

### **🧪 Test Mode**

Type `TEST EQUAL` (or WIN/LOSE) to automatically run 60 bets without user interaction. GUI stays visible but disabled. Useful for validating game logic and collecting baseline data quickly.

---

### **🔐 Critical Design Rules**

| Responsibility | Owner | Note |
|---|---|---|
| Set condition (EQUAL/WIN/LOSE) | `RemoteResearcher` only | No direct GUI calls |
| Enable metrics logging | `RemoteResearcher` only | Gates CSV recording |
| Increment bet counter | `on_spin()` or `_execute_spin_logic()` | Prevents count skips |
| All game logic | `core/slot_logic.py` | Single source of truth |

**These constraints prevent accidental state inconsistencies.**

---

### **🔢 Session Constants**

```python
INITIAL_BUDGET = 100 coins
MIN_BET = 0.10
MAX_BET = 2.0
BET_STEP = 0.10     # 20 increments available
TOTAL_SESSION_BETS = 60
PHASE_LENGTH = 20
```

---

### **🎬 Build System**

- **Manual mode**: Interactive prompt asks for condition every launch
- **Build mode**: `utils/build_config.py` bakes condition into executable
- **CSV naming**: Auto-increments per build to prevent overwrites  
  Example: `metrics_E_MEX1_1.csv`, `metrics_E_MEX1_2.csv`, etc.

---

### **📁 Project Structure**
```
├── main.py                           # Entry point
├── core/
│   ├── slot_logic.py                # ALL game logic & reward tables
│   ├── metrics_logger.py            # CSV append-only logger
│   ├── remote_researcher.py         # Condition & test mode control
│   ├── sound_manager.py             # Audio playback
│   └── redeem_logic.py              # One-time codes
├── gui/
│   ├── main_window.py               # PyQt5 UI + session loop
│   ├── redeem_dialog.py             # Redeem popup
│   └── assets/                      # Icons, sounds, music
├── utils/
│   ├── file_manager.py              # Safe path resolution
│   └── build_config.py              # BUILD_CONDITION, MESSAGE_TYPE
└── data/
    └── metrics_*.csv                # Auto-created CSV per session
```

---
