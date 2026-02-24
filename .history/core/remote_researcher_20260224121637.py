from core import metrics_logger
from core.slot_logic import update_condition

VALID_CONDITIONS = ["EQUAL", "WIN", "LOSE"]  # EQUAL, WIN, LOSE

class RemoteResearcher:
    """Gestisce i parametri di sessione forniti dal ricercatore solo prima dell'esecuzione.

    Args:
        metrics_logger: Istanza condivisa di MetricsLogger.
    """

    def __init__(self, metrics_logger) -> None:
        self._metrics_logger = metrics_logger
        self._current_condition: str = "EQUAL"  # valore di default EQUAL (gli altri sono "WIN" e "LOSE")
        self._input_data: str = ""
        self._test_mode: bool = False  # se True, avvia testing_statistics automatico

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def test_mode(self) -> bool:
        """True se il ricercatore ha attivato la modalità TEST."""
        return self._test_mode

    # ------------------------------------------------------------------
    # Setup iniziale (chiamato prima di window.show())
    # ------------------------------------------------------------------

    # COMPLETO
    def set_input_data(self) -> None:
        """Raccoglie i parametri iniziali dal ricercatore via terminale.

        Inserire 'TEST' come dato per attivare la modalità di test automatico.
        """
        self._input_data = input("Insert CONDITION (or 'TEST' for automated test): ").strip()
        input("Press ENTER to start application with CONDITION: " + self._input_data)

        if self._input_data.upper() == "TEST":
            # TEST_MODE: set_expected_value non viene chiamato qui;
            # sarà testing_statistics a iterare su tutti i valori.
            self._test_mode = True
            print("[RemoteResearcher] TEST_MODE abilitato.")
        else:
            # Imposta condition iniziale tramite il metodo autorizzato
            self.set_condition(self._input_data)
            print(f"[RemoteResearcher] Avvio con INPUT={self._input_data} CONDITION={self._current_condition}")


    def start_metrics(self) -> None:
        """Log SESSION_START e abilita le metriche con l'expected value corrente.

        In TEST_MODE usa il primo valore di CONVERTING_TABLE come placeholder;
        testing_statistics sovrascriverà expected_value spin per spin.
        """
        self._metrics_logger.log_session_start()
        if not self._test_mode:
            self._metrics_logger.enable_metrics(expected_value=self._current_expected_value)


    # ------------------------------------------------------------------
    # Aggiornamento condition — UNICO punto autorizzato
    # ------------------------------------------------------------------

    def set_condition(self, condition: str) -> None:
        """Aggiorna la condition iniziale del gioco.

        Args:
            condition: Stringa che rappresenta la condition (es. "EQUAL", "WIN", "LOSE").

        Raises:
            ValueError: Se condition non è in VALID_CONDITIONS.
        """
        if condition not in VALID_CONDITIONS:
            raise ValueError(
                f"[RemoteResearcher] condition '{condition}' non valida. "
                f"Valori consentiti: {VALID_CONDITIONS}"
            )
        self._current_condition = condition
        update_condition(condition)  # UNICA chiamata autorizzata: update_condition ha il ruolo di impostare i parametri interni in base alla CONDITION ricevuta

    def get_current_expected_value(self) -> float:
        """Ritorna il valore atteso corrente."""
        return self._current_expected_value

    # ------------------------------------------------------------------
    # Remote event stubs (futura integrazione TCP)
    # ------------------------------------------------------------------

    def remote_change_expected_value(self, new_expected_value: float) -> None:
        """Stub: aggiorna expected_value da remoto (es. via TCP)."""
        self.set_expected_value(new_expected_value)  # passa dal metodo autorizzato
        self._metrics_logger.log_remote_change_expected_value(new_expected_value)

    def remote_charge_coin(self, amount: float, current_coins: float) -> None:
        """Stub: aggiunge coins da remoto (es. via TCP)."""
        self._metrics_logger.log_remote_charge_coin(amount=amount, coin_after=current_coins)

    def remote_send_message(self, message: str) -> None:
        """Stub: invia un messaggio da remoto (es. via TCP)."""
        self._metrics_logger.log_remote_message(message)