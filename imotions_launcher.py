import subprocess
import pathlib
import sys
import time

if getattr(sys, 'frozen', False):
    exe_dir = pathlib.Path(sys.executable).parent
else:
    exe_dir = pathlib.Path(__file__).parent / "dist"

TARGET_EXE = exe_dir / "SlotMachine_TEST.exe"

def send_shift_pagedown():
    """Send Shift+PageDown via PowerShell SendKeys — hidden window, no visible terminal."""
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
        f.write(f"Error: {e}\n")
        f.write(f"Looking for: {TARGET_EXE}\n")
        f.write(f"Exists: {TARGET_EXE.exists()}\n")
    sys.exit(1)
