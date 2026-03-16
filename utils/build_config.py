"""
Creato così che dopo aver eseguito il build_all.py, ogni build avrà un file config/build.env incluso nel bundle, 
con dentro la config specifica di quella build (BUILD_CONDITION e MESSAGE_TYPE).
Cosa contiene dunque un .exe: a runtime eseguirà internamente build_config.py per leggere l'.env bundled assieme all'intera app 
    Returns:
        _type_: _description_
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