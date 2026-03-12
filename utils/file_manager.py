import json
import os
import sys

# ---------------------------------------------------------
#  PATH HANDLING
# ---------------------------------------------------------

def get_path(*paths) -> str:
    """Absolute path to a READ-ONLY bundled asset (images, sounds, QSS, etc.).

    - Normal run : relative to the project root.
    - Frozen exe : relative to sys._MEIPASS (PyInstaller temp extraction dir).
    When a bundled app starts up, the bootloader sets the sys.frozen attribute and 
    stores the absolute path to the bundle folder in sys._MEIPASS
    """
    
    if getattr(sys, 'frozen', False): # se l'app è bundled = "frozen" -> tutto in MEIPASS
        base_dir = sys._MEIPASS
        print('running in a PyInstaller bundle')
    else:
        base_dir = os.path.dirname(os.path.dirname(__file__))  # project root
    return os.path.join(base_dir, *paths)


# PER FILE PERSISTENTI = metrics.csv (NON IMMAGINI)
def get_writable_path(*paths) -> str:
    """Absolute path for files that must PERSIST across runs (e.g. metrics.csv).

    - Normal run : project root (same as get_path).
    - Frozen exe : next to the .exe. sys._MEIPASS is deleted on exit, so
                   runtime-written files must live outside it.
    
    se l'app è bundled (è buildata), il MEIPASS è temporaneo e poi cancellato.
    Allora devo salvare i file .csv nella directory sys.executable, usata quando ho le build.
    che punta all'eseguibile (Slot_Machine.exe) e quindi alla cartella in cui si trova (dist). 
    - Se app è bundled, le metriche vengono salvate in una posizione persistente (dist/metrics.csv) e non nel MEIPASS temporaneo. 
    - Se invece non è bundled, rimane tutto come prima, con i file salvati nella directory del progetto.
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable) # base_dir = /dist, qui messi: Slot_Machine.exe, metrics.csv
    else:
        base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, *paths)



# OLD BEFORE BUILD
'''def get_path(*paths) -> str:
    """
    Create an absolute path relative to the project root.
    Example: get_path("data", "user_data.json")
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))  # project root:primo dirname trova path globale ../utils, secondo sale fino a ../Slot_Machine
    return os.path.join(base_dir, *paths)
'''


# ---------------------------------------------------------
#  JSON LOADING / SAVING
# ---------------------------------------------------------

def load_json(path: str, default=None):
    """
    Safely load a JSON file.
    Returns `default` if the file does not exist or is invalid.
    """
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path: str, data: dict):
    """
    Safely write to a JSON file.
    Creates missing directories automatically.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)
