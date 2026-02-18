"""CSV metrics logger for the Slot Machine application.

Columns: TIMESTAMP | EVENT_TYPE | BET | EXPECTED_VALUE | RESULT | COIN | MESSAGE

Rules:
- Append-only: rows are never modified after writing.
- Only the USER application writes to this file.
- Internal events (SESSION_START, SESSION_END, BET, RESULT) are always available.
- Experiment events (START_METRICS, MESSAGE, CHANGE_EXPECTED_VALUE, CHARGE_COIN)
  require metrics to be enabled first via start_metrics().
"""
import csv
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
_metrics_enabled: bool = False
_current_expected_value: float = 0.0

CSV_PATH: str = "metrics.csv"
COLUMNS: list[str] = ["TIMESTAMP", "EVENT_TYPE", "BET", "EXPECTED_VALUE", "RESULT", "COIN", "MESSAGE"]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _timestamp() -> str:
    """Returns current time as ISO-like string: YYYY-MM-DD HH:MM:SS"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _ensure_header() -> None:
    """Creates the CSV file with header if it does not already exist."""
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(COLUMNS)


def _append_row(
    event_type: str,
    bet: str = "",
    expected_value: str = "",
    result: str = "",
    coin: str = "",
    message: str = "",
) -> None:
    """Appends a single row to the CSV. Never overwrites existing rows."""
    _ensure_header()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([_timestamp(), event_type, bet, expected_value, result, coin, message])


# ---------------------------------------------------------------------------
# State accessors
# ---------------------------------------------------------------------------
def is_metrics_enabled() -> bool:
    return _metrics_enabled


def get_current_expected_value() -> float:
    return _current_expected_value


# ---------------------------------------------------------------------------
# Internal events — always logged regardless of metrics flag
# ---------------------------------------------------------------------------
def log_session_start() -> None:
    """Log SESSION_START. Called once when the application launches."""
    _append_row("SESSION_START")


def log_session_end() -> None:
    """Log SESSION_END. Called once when the application closes."""
    _append_row("SESSION_END")


# ---------------------------------------------------------------------------
# Internal events — logged only when metrics are enabled
# ---------------------------------------------------------------------------
def log_bet(bet: float, coin_before: float) -> None:
    """Log a BET event. coin_before is the balance before deducting the bet."""
    if not _metrics_enabled:
        return
    _append_row(
        "BET",
        bet=f"{bet:.2f}",
        expected_value=str(_current_expected_value),
        coin=f"{coin_before:.2f}",
    )


def log_result(result_str: str, coin_after: float) -> None:
    """Log a RESULT event.

    result_str must be one of:
        WIN_3_MATCH_+<gain>  e.g. WIN_3_MATCH_+10.00
        WIN_2_MATCH_+<gain>  e.g. WIN_2_MATCH_+0.50
        LOSS
    """
    if not _metrics_enabled:
        return
    _append_row(
        "RESULT",
        expected_value=str(_current_expected_value),
        result=result_str,
        coin=f"{coin_after:.2f}",
    )


# ---------------------------------------------------------------------------
# Remote-command event stubs
# These functions are called by command_handler.py when TCP commands arrive.
# For now they contain only logging logic; GUI updates are handled via signals.
# ---------------------------------------------------------------------------
def start_metrics(expected_value: float) -> None:
    """Enable metrics and set the initial expected value.

    Called when START_METRICS <value> is received from the researcher.
    Updates WIN_PERCENTAGE in slot_logic via receive_expected_value().
    """
    global _metrics_enabled, _current_expected_value
    _metrics_enabled = True
    _current_expected_value = expected_value
    # Update slot win probability to match the expected value
    from core.slot_logic import receive_expected_value
    receive_expected_value(expected_value)
    _append_row("START_METRICS", expected_value=str(expected_value))


def log_change_expected_value(expected_value: float) -> None:
    """Update expected value mid-session and log it.

    Called when SET_EV <value> is received from the researcher.
    """
    global _current_expected_value
    _current_expected_value = expected_value
    from core.slot_logic import receive_expected_value
    receive_expected_value(expected_value)
    if _metrics_enabled:
        _append_row("CHANGE_EXPECTED_VALUE", expected_value=str(expected_value))


def log_charge_coin(coin_after: float) -> None:
    """Log a CHARGE_COIN event after the GUI balance has been updated.

    Called when SET_COINS <value> is received from the researcher.
    """
    if _metrics_enabled:
        _append_row("CHARGE_COIN", coin=f"{coin_after:.2f}")


def log_message(message: str) -> None:
    """Log a MESSAGE event sent by the researcher.

    Called when SEND_MSG <text> is received from the researcher.
    """
    if _metrics_enabled:
        _append_row("MESSAGE", message=message)
