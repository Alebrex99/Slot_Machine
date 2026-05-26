import subprocess, pathlib

ROOT = pathlib.Path(__file__).parent.parent

try:
    subprocess.run([
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=imotions_launcher",
        f"--distpath={ROOT / 'dist'}",
        f"--workpath={ROOT / 'build' / 'pyinstaller_work'}",
        f"--specpath={ROOT / 'build'}",
        str(ROOT / "imotions_launcher.py"),
    ], check=True, cwd=ROOT)
    print("✓ Built imotions_launcher.exe")
except Exception as e:
    print(f"✗ Build failed: {e}")

print("\nDone.")
