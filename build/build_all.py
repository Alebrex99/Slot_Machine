import subprocess, re, pathlib, shutil

# The bundled app does not include any source code. However, 
# PyInstaller bundles compiled Python scripts (.pyc files). 
# These could in principle be decompiled to reveal the logic of your code.

# __file__ : se non budled è semplice path relativo, quando Bundled è settato al correct path relativo al folder budled, es. sys._MEIPASS + 'mypackage/mymodule.py'
# pathlib.Path vs. os.path: il primo è più nuovo, Path crea un oggetto path su cui chiamare metodi

ROOT   = pathlib.Path(__file__).parent.parent   # project root regardless of CWD -> path globali ../build -> ../Slot_Machine
CONST  = ROOT / "core" / "constants.py" # usando / con pathlib fa in automatico il join = os.path.join(ROOT, "core", "constants.py")
# ROOT = Slot_Machine/
# CONST = Slot_Machine/core/constants.py

BUILDS = [
    ("W", "MEX1"), ("W", "MEX2"),
    ("L", "MEX1"), ("L", "MEX2"),
    ("E", "MEX1"), ("E", "MEX2"),
]

original = CONST.read_text(encoding="utf-8") # Converte tutto il file constants.py in una stringa

# Scrivi la costante BUILD_CONDITION e MESSAGE_TYPE in constants.py
for condition, mex in BUILDS:
    # Patch constants.py
    # prende l'intera stringa coincidente al file (original) -> cerca espressione regolare (tratta / come char semplici)
    # match con BUILD_CONDITION -> N spazi possibili ripetuti (\s*) -> : -> qualunque cosa ma minima possibile (.*?), cioè str -> 
    # = -> spazi ripetuti -> qualunque cosa, anche N parole, fuori dal gruppo chiuso tra (...) (.*)
    # inserisce qualunque al gruppo 1, ovvero "condition"
    patched = re.sub(r'(BUILD_CONDITION\s*:.*?=\s*).*', rf'\g<1>"{condition}"', original) # ritorna stringa sostituita solo nella parte trovata, il resto è identico all'originale
    patched = re.sub(r'(MESSAGE_TYPE\s*:.*?=\s*).*',    rf'\g<1>"{mex}"',       patched)
    CONST.write_text(patched, encoding="utf-8")

    # Delete __pycache__ for constants so PyInstaller picks up the patched .py,
    # not a stale .pyc from the previous build.
    # perchè Python + Pyinstaller potrebbero usare the cached .pyc invece di rileggere il .py
    # cancellare le caches forza a fare sempre fresh compile dei .py modificati
    cache = ROOT / "core" / "__pycache__"
    for f in cache.glob("constants*.pyc"): # dalle cache trova tutti i file che iniziano con constants e finiscono con .pyc; sono dei file precompilati (c) in cache
        f.unlink() # uguale a os.remove(), cancella i file .pyc di constants

    name = f"SlotMachine_{condition}_{mex}" # es. SlotMachine_W_MEX1.exe
    # sostituisce i vecchi os.system() and spawn(), chiama un processo nuovo
    subprocess.run([                            
        "pyinstaller",
        "--clean",                             # clear PyInstaller's own build cache -> cancella solo cache Pyinstaller
        "--onefile",                           # creato 1 solo file .exe
        "--windowed",                          # non usata la console (CMD) per la GUI, in quanto l'app è windowed, ovvero ha una sua GUI                  
        f"--name={name}",                      # nome dell'eseguibile finale, es. SlotMachine_W_MEX1.exe
        f"--distpath={ROOT / 'dist'}",         # dove mettere l'app bundled (default ./dist)
        f"--workpath={ROOT / 'build' / 'pyinstaller_work'}",          # dove vanno i file temporanei (default ./build)
        f"--specpath={ROOT / 'build'}",                               # dove mettere il file .spec generato da PyInstaller (default ./build)
        "--add-data", f"{ROOT / 'gui' / 'assets'};gui/assets",        # di norma PyInstaller include solo i .py, con --add-data posso includere anche cartelle/file extra (es. assets) -> "source;destination" -> include tutto il folder assets e lo mette in gui/assets dentro l'app bundled
        "--add-data", f"{ROOT / 'gui' / 'styles'};gui/styles",
        "--add-data", f"{ROOT / 'data' / 'redeem_codes.json'};data",
        "--collect-all", "pygame",                                    # include nel budled tutto il package pygame, Pyinstaller non lo fa in automatico
        str(ROOT / "main.py"),                  # entry point script
    ], check=True, cwd=ROOT) 
    # *args -> [...list]
    #check=True blocca il processo se c'è errore altrimenti si creano build non funzionanti
    # cwd = ROOT directory esecuzione comando

    print(f"✓ Built {name}")

# Restore constants.py to dev state
CONST.write_text(original, encoding="utf-8")
print("\nDone. constants.py restored to dev state.")