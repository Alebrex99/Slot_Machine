import subprocess, pathlib

ROOT = pathlib.Path(__file__).parent.parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

# 6 production builds — no E condition
BUILDS = [
    ("W", "MEX1"),
    ("W", "MEX2"),
    ("W", "NO_MEX"),
    ("L", "MEX1"),
    ("L", "MEX2"),
    ("L", "NO_MEX"),
]

# ── Templates ────────────────────────────────────────────────────────────────
# {EXE_NAME} is the only placeholder — replaced via .replace(), no escaping needed

BAT_TEMPLATE = """\
@echo off
cd /d "%~dp0"
start /wait "" "%~dp0{EXE_NAME}.exe"
timeout /t 1 /nobreak >nul
powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('+{PGDN}')"
"""

LAUNCHER_TEMPLATE = """\
import subprocess
import pathlib
import sys
import time

if getattr(sys, 'frozen', False):
    exe_dir = pathlib.Path(sys.executable).parent
else:
    exe_dir = pathlib.Path(__file__).parent / "dist"

TARGET_EXE = exe_dir / "{EXE_NAME}.exe"

def send_shift_pagedown():
    \"\"\"Send Shift+PageDown via PowerShell SendKeys — hidden window, no visible terminal.\"\"\"
    subprocess.run([
        'powershell', '-WindowStyle', 'Hidden', '-Command',
        "Add-Type -AssemblyName System.Windows.Forms; "
        "[System.Windows.Forms.SendKeys]::SendWait('+{PGDN}')"
    ], creationflags=subprocess.CREATE_NO_WINDOW)

try:
    if not TARGET_EXE.exists():
        raise FileNotFoundError(f"Target exe not found at {TARGET_EXE}")

    subprocess.run([str(TARGET_EXE)])   # blocks until the exe exits (any reason)

    time.sleep(1)           # give iMotions time to regain window focus
    send_shift_pagedown()   # advance iMotions to next stimulus

except Exception as e:
    with open(exe_dir / "launcher_error.log", "w") as f:
        f.write(f"Error: {e}\\n")
        f.write(f"Looking for: {TARGET_EXE}\\n")
        f.write(f"Exists: {TARGET_EXE.exists()}\\n")
    sys.exit(1)
"""

# ── Build loop ────────────────────────────────────────────────────────────────
for condition, mex in BUILDS:
    exe_name     = f"SlotMachine_{condition}_{mex}"   # e.g. SlotMachine_W_MEX1
    launcher_name = f"launcher_{condition}_{mex}"      # e.g. launcher_W_MEX1

    # 1. Write .bat file
    bat_path = DIST / f"bat_{launcher_name}.bat"
    bat_path.write_text(BAT_TEMPLATE.replace("{EXE_NAME}", exe_name), encoding="utf-8")
    print(f"  [BAT]  {bat_path.name}")

    # 2. Write temporary launcher .py (deleted after build)
    temp_src = ROOT / f"_temp_{launcher_name}.py"
    temp_src.write_text(LAUNCHER_TEMPLATE.replace("{EXE_NAME}", exe_name), encoding="utf-8")

    # 3. Build launcher .exe
    try:
        subprocess.run([
            "pyinstaller",
            "--clean",
            "--onefile",
            "--windowed",
            f"--name={launcher_name}",
            f"--distpath={DIST}",
            f"--workpath={ROOT / 'build' / 'pyinstaller_work'}",
            f"--specpath={ROOT / 'build'}",
            str(temp_src),
        ], check=True, cwd=ROOT)
        print(f"  [EXE]  {launcher_name}.exe")
    finally:
        if temp_src.exists():
            temp_src.unlink()   # always clean up temp source

print("\nDone. All 6 launchers built.")
print("Next step: open dist/ and convert each .bat with your Bat-to-Exe tool.")
