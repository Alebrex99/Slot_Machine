import subprocess, pathlib

# APP LAUNCHER BUILD

ROOT   = pathlib.Path(__file__).parent.parent

try:
    subprocess.run([
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=app_launcher",
        f"--distpath={ROOT / 'dist'}",
        f"--workpath={ROOT / 'build' / 'pyinstaller_work'}",
        f"--specpath={ROOT / 'build'}",
        str(ROOT / "app_launcher.py"),
    ], check=True, cwd=ROOT)
    print("✓ Built app_launcher.exe")
except Exception as e:
    print(f"✗ Build failed: {e}")
finally:
    pass

print("\nDone.")
