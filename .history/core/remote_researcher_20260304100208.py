# FIX: removed 'from core import metrics_logger' — the module was never used directly
# and the bare import shadows the constructor parameter of the same name, causing confusion.
from core.slot_logic import update_condition
from core.constants import VALID_CONDITIONS

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

        Inserire 'TEST + CONDITION' come dato per attivare la modalità di test automatico.
        """
        self._input_data = input("Insert CONDITION (or 'TEST + CONDITION' for automated test): ").strip()
        
        # TEST + CONDITION
        # l'utente può inserire "TEST EQUAL / E" o "TEST WIN / W" o "TEST LOSE / L" per attivare la modalità di test automatico con la condition desiderata
        # lettura dell'intera stringa inserita
        if self._input_data.upper().startswith("TEST "):
            parts = self._input_data.upper().split() # es. "TEST EQUAL" -> ["TEST", "EQUAL"]
            if len(parts) != 2:
                print("[RemoteResearcher] Formato input non valido per TEST_MODE. Usa 'TEST + CONDITION' (es. 'TEST EQUAL').")
                self.set_input_data()  # richiede input finché non valido
                return
            
            condition_part = parts[1]
            if condition_part not in VALID_CONDITIONS and condition_part not in VALID_CONDITIONS.values():
                print(f"[RemoteResearcher] condition '{condition_part}' non valida. Valori consentiti: {VALID_CONDITIONS}")
                self.set_input_data()  # richiede input finché non valido
                return
            
            self._test_mode = True
            self.set_condition(condition_part)  # imposta la condition specificata dopo "TEST"
            print(f"[RemoteResearcher] TEST_MODE abilitato con CONDITION={self._current_condition}.")
            input("Press ENTER to start TEST with CONDITION: " + self._current_condition)
            return
        
        
        if self._input_data.upper() not in VALID_CONDITIONS and self._input_data.upper() not in VALID_CONDITIONS.values():
            print(f"[RemoteResearcher] condition '{self._input_data}' non valida. Valori consentiti: {VALID_CONDITIONS}")
            self.set_input_data()  # richiede input finché non valido
            return  # evita di proseguire con il valore non valido dello stack corrente
        
        self.set_condition(self._input_data)
        print(f"[RemoteResearcher] Avvio con INPUT={self._input_data} CONDITION={self._current_condition}")
        input("Press ENTER to start application with CONDITION: " + self._current_condition)



    def start_metrics(self) -> None:
        """Log SESSION_START e abilita le metriche con la condition corrente.

        Sempre eseguito, indipendentemente da test_mode.
        L'ordine CSV risultante è: SESSION_START → START_METRICS → BET×60 → SESSION_END.
        """
        self._metrics_logger.log_session_start()
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
        if input_data.upper() in VALID_CONDITIONS: #è la chiave (es. "E") che viene convertita in valore (es. "EQUAL")
            self._current_condition = VALID_CONDITIONS[input_data.upper()]
        else: # è direttamente la condition in forma estesa (es. "EQUAL")
            self._current_condition = input_data.upper()  # accetta anche la forma completa (es. "EQUAL")
        update_condition(self._current_condition)  # UNICA chiamata autorizzata: update_condition ha il ruolo di impostare i parametri interni in base alla CONDITION ricevuta


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