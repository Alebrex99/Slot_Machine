"""
Mentre avviene l'esecuzione di build_all.py, runtime ogni build avrà un file config/build.env incluso nel bundle, 
con dentro la config specifica di quella build (BUILD_CONDITION e MESSAGE_TYPE).
- quando eseguo la build_all.py -> preparazione .env
- esecuzione pyinstaller -> avvia main.py -> partendo dagli import in main.py
- la catena di import arriva a from utils.build_config -> Python carica ed esegue il codice che prepara solo BUILD_CONDITION e MESSAGE_TYPE leggendo .env
"""

import os

from core.constants import BUILD_CONDITION as DEFAULT_BUILD_CONDITION
from core.constants import MESSAGE_TYPE as DEFAULT_MESSAGE_TYPE
from core.constants import VALID_CONDITIONS
from utils.file_manager import get_path

_BUILD_ENV_PATH = ("config", "build.env")
_VALID_BUILD_CONDITIONS = VALID_CONDITIONS
_VALID_MESSAGE_TYPES = {"MEX1", "MEX2"}


def _read_env_file() -> dict[str, str]:
    """
    Read environment variables from a configuration file.
    Parses a .env file and extracts key-value pairs, ignoring comments and empty lines.
    Values are stripped of surrounding quotes (both single and double) and whitespace.
    Returns:
        dict[str, str]: A dictionary containing environment variable key-value pairs.
                       Returns an empty dictionary if the file does not exist.
    File Format:
        - Lines starting with '#' are treated as comments and ignored
        - Empty lines are ignored
        - Lines must contain '=' to be parsed
        - Format: KEY=VALUE or KEY="VALUE" or KEY='VALUE'
    """
    env_path = get_path(*_BUILD_ENV_PATH)

    if not os.path.exists(env_path):
        return {}

    values: dict[str, str] = {}

    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")

    return values


_env_values = _read_env_file()

_build_condition = _env_values.get("BUILD_CONDITION", DEFAULT_BUILD_CONDITION)
_message_type = _env_values.get("MESSAGE_TYPE", DEFAULT_MESSAGE_TYPE)

BUILD_CONDITION = (
    _build_condition
    if _build_condition in _VALID_BUILD_CONDITIONS or _build_condition in _VALID_BUILD_CONDITIONS.values()
    else DEFAULT_BUILD_CONDITION
)

MESSAGE_TYPE = (
    _message_type
    if _message_type in _VALID_MESSAGE_TYPES
    else DEFAULT_MESSAGE_TYPE
)