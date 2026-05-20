import subprocess
import pathlib
import sys

if getattr(sys, 'frozen', False):
    exe_dir = pathlib.Path(sys.executable).parent
else:
    exe_dir = pathlib.Path(__file__).parent / "dist"

TEST_EXE = exe_dir / "SlotMachine_TEST.exe"

try:
    if not TEST_EXE.exists():
        raise FileNotFoundError(f"SlotMachine_TEST.exe not found at {TEST_EXE}")

    subprocess.run([str(TEST_EXE)], check=True)
except Exception as e:
    with open(exe_dir / "launcher_error.log", "w") as f:
        f.write(f"Error: {e}\n")
        f.write(f"Looking for: {TEST_EXE}\n")
        f.write(f"Exists: {TEST_EXE.exists()}\n")
    sys.exit(1)
