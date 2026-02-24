from core import metrics_logger
from core.slot_logic import VALID_CONDITIONS, update_condition

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

    def set_input_data(self) -> None:
        """Raccoglie i parametri iniziali dal ricercatore via terminale.

        Inserire 'TEST' come dato per attivare la modalità di test automatico.
        """
        self._input_data = input("Insert CONDITION (or 'TEST' for automated test): ").strip()

        if self._input_data.upper() == "TEST":
            self._test_mode = True
            print("[RemoteResearcher] TEST_MODE abilitato.")
            return  # ← esce subito, nessuna condition da impostare

        # se input è "E", non si trova in chiavi oppure input "EQUAL" non si trova in valori, allora è un input non valido
        if self._input_data.upper() not in VALID_CONDITIONS and self._input_data.upper() not in VALID_CONDITIONS.values():
            print(f"[RemoteResearcher] condition '{self._input_data}' non valida. Valori consentiti: {VALID_CONDITIONS}")
            self.set_input_data()  # richiede input finché non valido
            return  # evita di proseguire con il valore non valido dello stack corrente
        self.set_condition(self._input_data)
        print(f"[RemoteResearcher] Avvio con INPUT={self._input_data} CONDITION={self._current_condition}")
        input("Press ENTER to start application with CONDITION: " + self._input_data)



    def start_metrics(self) -> None:
        """Log SESSION_START e abilita le metriche con la condition corrente.

        In TEST_MODE usa il primo valore di CONVERTING_TABLE come placeholder;
        testing_statistics sovrascriverà expected_value spin per spin.
        """
        self._metrics_logger.log_session_start()
        if not self._test_mode:
            self._metrics_logger.enable_metrics(condition=self._current_condition)


    # ------------------------------------------------------------------
    # Aggiornamento condition — UNICO punto autorizzato
    # ------------------------------------------------------------------

    def set_condition(self, input_data: str) -> None:
        """Aggiorna la condition iniziale del gioco.

        Args:
            input_data: Stringa che rappresenta la condition (es. "EQUAL", "WIN", "LOSE").
        Raises:
            set_input_data viene richiamato se condition non è valida, finché non viene fornita una condition valida.
        """
        if input_data.upper() in VALID_CONDITIONS:
            condition = VALID_CONDITIONS[input_data.upper()]
        else:
            condition = input_data.upper()  # accetta anche la forma completa (es. "EQUAL")
        self._current_condition = condition
        update_condition(condition)  # UNICA chiamata autorizzata: update_condition ha il ruolo di impostare i parametri interni in base alla CONDITION ricevuta


    def get_current_condition(self) -> str:
        """Ritorna la condition corrente."""
        return self._current_condition  
    
    
    
    # --------------------------------------------------------------------------------------
    # Remote event stubs (futura integrazione TCP) attuale è tutto da INPUT sulla stessa APP
    # --------------------------------------------------------------------------------------

    def remote_change_condition(self, new_condition: str) -> None:
        """Stub: aggiorna condition da remoto (es. via TCP)."""
        self.set_condition(new_condition)  # passa dal metodo autorizzato
        self._metrics_logger.log_remote_change_condition(new_condition)

    def remote_charge_coin(self, amount: float, current_coins: float) -> None:
        """Stub: aggiunge coins da remoto (es. via TCP)."""
        self._metrics_logger.log_remote_charge_coin(amount=amount, coin_after=current_coins)

    def remote_send_message(self, message: str) -> None:
        """Stub: invia un messaggio da remoto (es. via TCP)."""
        self._metrics_logger.log_remote_message(message)