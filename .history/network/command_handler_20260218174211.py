"""Remote command handler for the Slot Machine USER application.

This module is the single entry point for all commands received from
the RESEARCHER application. It will be called by the future TCP server.

For now (Step 1) only the pure logic is defined here — no socket code.
The TCP server (network/tcp_server.py) will import and call dispatch()
once networking is implemented.

Supported commands:
    START_METRICS <float>       Enable metrics and set expected value.
    SET_EV <float>              Change expected value mid-session.
    SET_COINS <float>           Update coin balance and GUI.
    SEND_MSG <text>             Display a message in the GUI.

GUI updates are performed via Qt signals emitted on the provided
signal_bridge object, so the socket thread never touches widgets directly.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imported only for type hints; avoids circular imports at runtime.
    from network.signal_bridge import SignalBridge

import core.metrics as metrics
from core.slot_logic import CONVERTING_TABLE


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
VALID_EXPECTED_VALUES: set[float] = set(CONVERTING_TABLE.keys())


def _parse_float(raw: str) -> float | None:
    """Convert a string to float, return None on failure."""
    try:
        return float(raw.strip().replace(",", "."))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Individual command handlers
# ---------------------------------------------------------------------------
def handle_start_metrics(raw_value: str, bridge: "SignalBridge") -> str:
    """Enable metrics collection and set the initial expected value.

    Usage: START_METRICS <expected_value>
    """
    value = _parse_float(raw_value)
    if value is None or value not in VALID_EXPECTED_VALUES:
        return f"ERROR: invalid expected value '{raw_value}'. Allowed: {sorted(VALID_EXPECTED_VALUES)}"

    metrics.start_metrics(value)
    # No GUI update needed for this command.
    return f"OK: metrics started, EV={value}"


def handle_set_ev(raw_value: str, bridge: "SignalBridge") -> str:
    """Change the expected value (and WIN_PERCENTAGE) during an active session.

    Usage: SET_EV <expected_value>
    """
    value = _parse_float(raw_value)
    if value is None or value not in VALID_EXPECTED_VALUES:
        return f"ERROR: invalid expected value '{raw_value}'. Allowed: {sorted(VALID_EXPECTED_VALUES)}"

    metrics.log_change_expected_value(value)
    return f"OK: expected value changed to {value}"


def handle_set_coins(raw_value: str, bridge: "SignalBridge") -> str:
    """Set the player's coin balance and request a GUI update via signal.

    Usage: SET_COINS <amount>
    """
    value = _parse_float(raw_value)
    if value is None or value < 0:
        return f"ERROR: invalid coin amount '{raw_value}'"

    # Emit signal so the GUI thread handles the update safely.
    bridge.set_coins_signal.emit(value)
    # Logging happens after the GUI confirms the update (see main_window.py).
    return f"OK: set coins to {value:.2f}"


def handle_send_msg(text: str, bridge: "SignalBridge") -> str:
    """Display a message in the GUI and log it.

    Usage: SEND_MSG <text>
    """
    if not text.strip():
        return "ERROR: empty message"

    metrics.log_message(text.strip())
    bridge.send_message_signal.emit(text.strip())
    return f"OK: message sent"


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------
def dispatch(raw_command: str, bridge: "SignalBridge") -> str:
    """Parse and dispatch a raw command string received from the researcher.

    Returns a response string to be sent back over TCP.
    """
    parts = raw_command.strip().split(" ", 1)
    cmd = parts[0].upper()
    arg = parts[1] if len(parts) > 1 else ""

    handlers = {
        "START_METRICS": handle_start_metrics,
        "SET_EV": handle_set_ev,
        "SET_COINS": handle_set_coins,
        "SEND_MSG": handle_send_msg,
    }

    if cmd not in handlers:
        return f"ERROR: unknown command '{cmd}'"

    return handlers[cmd](arg, bridge)
