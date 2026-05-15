import subprocess, pathlib

# TEST BUILD

ROOT   = pathlib.Path(__file__).parent.parent
BASE_ENV = ROOT / "config"
BUILD_ENV = BASE_ENV / "build.env"

try:
    BASE_ENV.mkdir(exist_ok=True)
    BUILD_ENV.write_text(        
        "BUILD_CONDITION=E\n" # va SCRITTA SEMPRE, altrimenti si finisce in MANUAL MODE
        "TEST_BUILD=true\n",
        encoding="utf-8")

    subprocess.run([
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=SlotMachine_TEST",
        f"--distpath={ROOT / 'dist'}",
        f"--workpath={ROOT / 'build' / 'pyinstaller_work'}",
        f"--specpath={ROOT / 'build'}",
        "--add-data", f"{ROOT / 'gui' / 'assets'};gui/assets",
        "--add-data", f"{ROOT / 'gui' / 'styles'};gui/styles",
        "--add-data", f"{BUILD_ENV};config",
        "--collect-all", "pygame",
        str(ROOT / "main.py"),
    ], check=True, cwd=ROOT)
    print("✓ Built SlotMachine_TEST")
finally:
    if BUILD_ENV.exists():
        BUILD_ENV.unlink()

print("\nDone.")
