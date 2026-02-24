"""
CSV-based metrics logger for the Slot Machine application.

Handles session lifecycle and gameplay event logging.
All writes are append-only and execute on the GUI thread.
"""

import csv
import os
from datetime import datetime
from typing import Optional

from core.slot_logic import VALID_CONDITIONS, update_condition

# CSV column headers
_CSV_COLUMNS = ["TIMESTAMP", "EVENT_TYPE", "BET_NUMBER" "BET", "INPUT_CONDITION", "RESULT", "COIN", "MESSAGE"]

# Default path for the metrics CSV file
_CSV_PATH = "data/metrics.csv"


class MetricsLogger:
    """Append-only CSV logger for slot machine session and gameplay events.

    Args:
        csv_path: Path to the output CSV file. Created if it does not exist.
    """

    def __init__(self, csv_path: str = _CSV_PATH) -> None:
        self._csv_path = csv_path
        self._metrics_enabled: bool = False
        self._current_condition: Optional[str] = None
        # Create file with headers if it does not exist
        if not os.path.exists(self._csv_path):
            self._write_row(_CSV_COLUMNS)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    # cosa fa @property: permette di accedere a un metodo 
    # come se fosse un attributo, senza doverlo chiamare con le parentesi.
    # es. metrics_logger.metrics_enabled invece di metrics_logger.metrics_enabled()
    @property
    def metrics_enabled(self) -> bool:
        """Returns whether gameplay event logging is active."""
        return self._metrics_enabled

    @property
    def current_condition(self) -> Optional[str]:
        """Returns the currently configured condition, or None."""
        return self._current_condition

    # Deve essere chiamata dal ricercatore esterno / testing
    def enable_metrics(self, condition: str) -> None:
        """Activates gameplay logging and configures the condition (logging version).

        Args:
            condition: Must exists in VALID_CONDITIONS.

        Raises:
            ValueError: If condition is not in VALID_CONDITIONS.
        """
        if condition not in VALID_CONDITIONS:
            raise ValueError(
                f"Invalid condition '{condition}'. "
                f"Allowed values: {VALID_CONDITIONS}"
            )

        self._current_condition = condition
        self._metrics_enabled = True

        self._log(
            event_type="START_METRICS",
            condition=condition,
        )

    def log_session_start(self) -> None:
        """Logs the SESSION_START event. Always executed regardless of metrics_enabled."""
        self._log(event_type="SESSION_START")

    def log_session_end(self) -> None:
        """Logs the SESSION_END event. Always executed regardless of metrics_enabled."""
        self._log(event_type="SESSION_END")

    def log_bet(self, bet: float, coin_before: float) -> None:
        """Logs a BET event. Only written when metrics_enabled is True.

        Args:
            bet: The bet amount placed by the user.
            coin_before: Coin balance before the spin is deducted.
        """
        if not self._metrics_enabled:
            return

        self._log(
            event_type="BET",
            bet_number=None,  # bet_number can be added if tracking bet count is implemented
            bet=bet,
            condition=self._current_condition,
            coin=coin_before,
        )

    def log_result(self, result_tuple: tuple, reward: float, bet_number: int, bet:float, coin_after: float) -> None:
        """Logs a RESULT event. Only written when metrics_enabled is True.

        Args:
            result_tuple: The 3-symbol tuple from spin_reels() e.g. ("cherry", "cherry", "lemon").
            reward: Computed reward after bet multiplier (0 if loss).
            bet_number: Current bet number.
            bet: The bet amount that was placed.
            coin_after: Coin balance after reward is applied.
        """
        if not self._metrics_enabled:
            return

        result_str = self._format_result(result_tuple, reward)

        self._log(
            event_type="RESULT",
            condition=self._current_condition,
            result=result_str,
            bet_number=bet_number,
            bet=bet,
            coin=coin_after,
        )

    # ------------------------------------------------------------------
    # Remote event stubs (not yet triggered externally)
    # ------------------------------------------------------------------

    def log_remote_message(self, message: str) -> None:
        """Logs a MESSAGE event received from the researcher application.

        Args:
            message: Arbitrary text message from the researcher.
        """
        self._log(event_type="MESSAGE", message=message)

    def log_remote_charge_coin(self, amount: float, coin_after: float) -> None:
        """Logs a CHARGE_COIN event sent by the researcher application.

        Args:
            amount: Amount of coins added remotely.
            coin_after: Coin balance after the charge.
        """
        self._log(event_type="CHARGE_COIN", coin=coin_after, message=f"added={amount:.2f}")

    def log_remote_change_expected_value(self, new_expected_value: float) -> None:
        """Logs a CHANGE_EXPECTED_VALUE event sent by the researcher application.

        Args:
            new_expected_value: New expected value applied by the researcher.

        Raises:
            ValueError: If new_expected_value is not in CONVERTING_TABLE.
        """
        if new_expected_value not in CONVERTING_TABLE:
            raise ValueError(
                f"Invalid expected_value '{new_expected_value}'. "
                f"Allowed values: {list(CONVERTING_TABLE.keys())}"
            )

        self._current_expected_value = new_expected_value

        self._log(
            event_type="CHANGE_EXPECTED_VALUE",
            expected_value=new_expected_value,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _format_result(self, result_tuple: tuple, reward: float) -> str:
        """Formats the result tuple into a human-readable result string.

        Args:
            result_tuple: 3-symbol tuple e.g. ("seven", "seven", "seven").
            reward: Computed reward value.

        Returns:
            A string like WIN_3_MATCH_+5.00, WIN_2_MATCH_+1.00, or LOSS.
        """
        r1, r2, r3 = result_tuple

        if r1 == r2 == r3:
            return f"WIN_3_MATCH_+{reward:.2f}"

        if r1 == r2 or r2 == r3 or r1 == r3:
            return f"WIN_2_MATCH_+{reward:.2f}"

        return "LOSS"

    def _log(
        self,
        event_type: str,
        bet_number: Optional[int] = None,
        bet: Optional[float] = None,
        condition: Optional[str] = None,
        result: Optional[str] = None,
        coin: Optional[float] = None,
        message: Optional[str] = None,
    ) -> None:
        """Writes a single row to the CSV file.

        Args:
            event_type: The type of event being logged.
            bet_number: Current bet number (optional).
            bet: Bet amount (optional).
            condition: Current condition (optional).
            result: Result string (optional).
            coin: Coin balance at time of event (optional).
            message: Additional message string (optional).
        """
        # mantieni fino ai centesimi
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]

        row = [
            timestamp,
            event_type,
            f"{bet_number}" if bet_number is not None else "",
            f"{bet:.2f}" if bet is not None else "",
            f"{condition}" if condition is not None else "",
            result or "",
            f"{coin:.2f}" if coin is not None else "",
            message or "",
        ]

        self._write_row(row)

    def _write_row(self, row: list) -> None:
        """Appends a single row to the CSV file.

        Args:
            row: List of values to write.
        """
        #apre + crea il file
        with open(self._csv_path, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(row)