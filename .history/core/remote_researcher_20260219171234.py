"""RemoteResearcher gestisce l'interazione con il ricercatore esterno.

E' l'UNICO responsabile di:
- chiamare update_expected_value() in slot_logic (modifica WIN_PERCENTAGE)
- abilitare le metriche tramite metrics_logger.enable_metrics()
- gestire la modalità TEST (TEST_MODE)

Non scrive direttamente sul CSV: delega tutto a MetricsLogger.
"""

from core.slot_logic import update_expected_value, CONVERTING_TABLE


class RemoteResearcher:
    """Gestisce i parametri di sessione forniti dal ricercatore prima dell'avvio della GUI.

    Args:
        metrics_logger: Istanza condivisa di MetricsLogger.
    """

    def __init__(self, metrics_logger) -> None:
        self._metrics_logger = metrics_logger
        self._current_expected_value: float = 0.33  # valore di default
        self._input_data: str = ""
        self._test_mode: bool = False  # se True, avvia testing_statistics automatico

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def test_mode(self) -> bool:
        """True se il ricercatore ha attivato la modalità TEST."""
        return self._test_mode

    @property
    def current_expected_value(self) -> float:
        """Ritorna il valore atteso corrente."""
        return self._current_expected_value

    # ------------------------------------------------------------------
    # Setup iniziale (chiamato prima di window.show())
    # ------------------------------------------------------------------

    def set_input_data(self) -> None:
        """Raccoglie i parametri iniziali dal ricercatore via terminale.

        Inserire 'TEST' come dato per attivare la modalità di test automatico.
        """
        self._input_data = input("Insert DATA (or 'TEST' for automated test): ").strip()
        input("Press ENTER to start application with DATA: " + self._input_data)

        if self._input_data.upper() == "TEST":
            # In TEST_MODE non serve impostare expected_value iniziale:
            # sarà testing_statistics a iterare tutti i valori
            self._test_mode = True
            print("[RemoteResearcher] TEST_MODE abilitato — la GUI sara' disabilitata durante il test.")
        else:
            # Imposta expected_value iniziale — UNICO punto che chiama update_expected_value
            self.set_expected_value(0.33)
            print(f"[RemoteResearcher] Avvio con expected_value={self._current_expected_value} DATA={self._input_data}")

    def start_metrics(self) -> None:
        """Log SESSION_START e abilita le metriche con l'expected value corrente.

        Chiamato dopo set_input_data() e prima di window.show().
        """
        self._metrics_logger.log_session_start()
        self._metrics_logger.enable_metrics(expected_value=self._current_expected_value)

    # ------------------------------------------------------------------
    # Aggiornamento expected value (UNICO punto autorizzato)
    # ------------------------------------------------------------------

    def set_expected_value(self, expected_value: float) -> None:
        """Aggiorna l'expected value: modifica WIN_PERCENTAGE in slot_logic.

        Questo e' l'UNICO metodo autorizzato a chiamare update_expected_value().

        Args:
            expected_value: Deve essere una chiave valida di CONVERTING_TABLE.

        Raises:
            ValueError: Se expected_value non e' in CONVERTING_TABLE.
        """
        if expected_value not in CONVERTING_TABLE:
            raise ValueError(
                f"[RemoteResearcher] expected_value '{expected_value}' non valido. "
                f"Valori consentiti: {list(CONVERTING_TABLE.keys())}"
            )
        self._current_expected_value = expected_value
        update_expected_value(expected_value)  # UNICA chiamata autorizzata

    def get_current_expected_value(self) -> float:
        """Ritorna il valore atteso corrente."""
        return self._current_expected_value

    # ------------------------------------------------------------------
    # Remote event stubs (futura integrazione TCP)
    # ------------------------------------------------------------------

    def remote_change_expected_value(self, new_expected_value: float) -> None:
        """Stub: aggiorna l'expected value da remoto (es. via TCP)."""
        self.set_expected_value(new_expected_value)
        self._metrics_logger.log_remote_change_expected_value(new_expected_value)

    def remote_charge_coin(self, amount: float, current_coins: float) -> None:
        """Stub: aggiunge coins da remoto (es. via TCP)."""
        self._metrics_logger.log_remote_charge_coin(amount=amount, coin_after=current_coins)

    def remote_send_message(self, message: str) -> None:
        """Stub: invia un messaggio da remoto (es. via TCP)."""
        self._metrics_logger.log_remote_message(message)