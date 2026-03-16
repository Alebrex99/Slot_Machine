import subprocess, pathlib

ROOT   = pathlib.Path(__file__).parent.parent   # project root regardless of CWD -> path globali ../build -> ../Slot_Machine
BASE_ENV = ROOT / "config"
BUILD_ENV = BASE_ENV / "build.env"

BUILDS = [
    ("W", "MEX1"), ("W", "MEX2"),
    ("L", "MEX1"), ("L", "MEX2"),
    ("E", "MEX1"), ("E", "MEX2"),
]


try: 
    for condition, mex in BUILDS:
        if not BUILD_ENV.exists():
            BASE_ENV.mkdir(exist_ok=True) # crea la cartella config se non esiste
            BUILD_ENV.touch() # crea il file build.env se non esiste        
        # ogni volta sostituisce il contenuto di build.env
        BUILD_ENV.write_text( 
            f"BUILD_CONDITION={condition}\n"
            f"MESSAGE_TYPE={mex}\n",
            encoding="utf-8",
        )
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
            "--add-data", f"{BUILD_ENV};config",    # inlude build.env in the bundle, so the bundled app can read its config (BUILD_CONDITION and MESSAGE_TYPE) at runtime from the same file used in dev
            "--collect-all", "pygame",              # include nel budled tutto il package pygame, Pyinstaller non lo fa in automatico
            str(ROOT / "main.py"),                  # entry point script
        ], check=True, cwd=ROOT) 
        # *args -> [...list]
        # check=True blocca il processo se c'è errore altrimenti si creano build non funzionanti
        # cwd = ROOT directory esecuzione comando
        print(f"✓ Built {name}")
finally:
    if BUILD_ENV.exists():
       BUILD_ENV.unlink() # cancella il file build.env dopo tutte le build, per pulizia (non serve più, era solo per comunicare la config alle build)

print("\nDone. BUILD_ENV restored to dev state.")