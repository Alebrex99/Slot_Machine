import subprocess, re, pathlib, shutil

ROOT   = pathlib.Path(__file__).parent.parent   # project root regardless of CWD
CONST  = ROOT / "core" / "constants.py"

BUILDS = [
    ("W", "MEX1"), ("W", "MEX2"),
    ("L", "MEX1"), ("L", "MEX2"),
    ("E", "MEX1"), ("E", "MEX2"),
]

original = CONST.read_text(encoding="utf-8")

for condition, mex in BUILDS:
    # Patch constants.py
    patched = re.sub(r'(BUILD_CONDITION\s*:.*?=\s*).*', rf'\g<1>"{condition}"', original)
    patched = re.sub(r'(MESSAGE_TYPE\s*:.*?=\s*).*',    rf'\g<1>"{mex}"',       patched)
    CONST.write_text(patched, encoding="utf-8")

    # Delete __pycache__ for constants so PyInstaller picks up the patched .py,
    # not a stale .pyc from the previous build.
    cache = ROOT / "core" / "__pycache__"
    for f in cache.glob("constants*.pyc"):
        f.unlink()

    name = f"SlotMachine_{condition}_{mex}"
    subprocess.run([
        "pyinstaller",
        "--clean",                               # clear PyInstaller's own build cache
        "--onefile",
        "--windowed",
        f"--name={name}",
        f"--distpath={ROOT / 'dist'}",
        f"--workpath={ROOT / 'build' / 'pyinstaller_work'}",
        f"--specpath={ROOT / 'build'}",
        "--add-data", f"{ROOT / 'gui' / 'assets'};gui/assets",
        "--add-data", f"{ROOT / 'gui' / 'styles'};gui/styles",
        "--add-data", f"{ROOT / 'data' / 'redeem_codes.json'};data",
        "--collect-all", "pygame",
        str(ROOT / "main.py"),
    ], check=True, cwd=ROOT)

    print(f"✓ Built {name}")

# Restore constants.py to dev state
CONST.write_text(original, encoding="utf-8")
print("\nDone. constants.py restored to dev state.")