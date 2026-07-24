# SLOT_MACHINE — How to Use

## Folder Structure

```
SLOT_MACHINE/
  BUILDS/
    ENG/          ← all English application builds (.exe)
    ESP/          ← all Spanish application builds (.exe)
  LAUNCHERS/
    W_MEX1/       ← launchers + application build must be placed here
    W_MEX2/
    W_NO_MEX/
    L_MEX1/
    L_MEX2/
    L_NO_MEX/
    TEST/
```

---

## Setup — Before Running in iMotions

1. **Choose the language** (ENG or ESP) and open the corresponding `BUILDS/` subfolder.

2. **Copy the application `.exe`** into its matching `LAUNCHERS/` subfolder:

   | Application build | Copy into |
   |---|---|
   | `SlotMachine_W_MEX1.exe` | `LAUNCHERS/W_MEX1/` |
   | `SlotMachine_W_MEX2.exe` | `LAUNCHERS/W_MEX2/` |
   | `SlotMachine_W_NO_MEX.exe` | `LAUNCHERS/W_NO_MEX/` |
   | `SlotMachine_L_MEX1.exe` | `LAUNCHERS/L_MEX1/` |
   | `SlotMachine_L_MEX2.exe` | `LAUNCHERS/L_MEX2/` |
   | `SlotMachine_L_NO_MEX.exe` | `LAUNCHERS/L_NO_MEX/` |
   | `SlotMachine_TEST.exe` | `LAUNCHERS/TEST/` |

   ⚠️ **The application `.exe` MUST be in the same folder as the launcher.**

---

## Linking into iMotions

Inside each `LAUNCHERS/` subfolder you will find two launcher options — pick one:

| File | Notes |
|---|---|
| `launcher_X_Y.exe` | PyInstaller build — no console window |
| `bat_launcher_X_Y.exe` | Bat-to-Exe build — no console window |

In iMotions, add the chosen launcher `.exe` as the item for that condition.

**What the launcher does automatically:**
1. Starts the slot machine application and waits for it to finish
2. Sends **Shift + Page Down** to iMotions to advance to the next page

---

## Replacing a Build

If you need to update an application build, simply replace the `.exe` inside the
corresponding `LAUNCHERS/` subfolder with the new one.
**The launchers never need to be replaced or reconfigured.**
