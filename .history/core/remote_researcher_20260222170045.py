'''Costruzione di una classe RemoteResearcher che gestisce 
l'interazione con il ricercatore esterno, inclusi input, log iniziale e 
abilitazione metriche. Questa classe può essere utilizzata in main.py 
per semplificare la gestione del flusso di lavoro del ricercatore.

Il ricercatore esterno agisce, prima dell'inizio della renderizzazione della GUI, 
fornisce i parametri in input che stabiliscono quando avverranno:
- log iniziale (session start)
- abilitazione metriche, chiamando enable_metrics() con il valore desiderato di expected_value (es. 0.33)
- specifica di quando visualizzare i messaggi (in quali momenti precisi) e log messaggi
- specifica di quando, durante il gioco, modificare l'expected value (es. tempo partecipante = 10 minuti, per 2 min valore atteso 1, per 4 min 3, per 4 min 0.67, ecc..)
- specifica di quando, durante il gioco, avviene il caricamentento dei coins'''

from core import metrics_logger
from core.slot_logic import update_expected_value, CONVERTING_TABLE


class RemoteResearcher:
    """Gestisce i parametri di sessione forniti dal ricercatore prima e durante l'esecuzione.

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
            # TEST_MODE: set_expected_value non viene chiamato qui;
            # sarà testing_statistics a iterare su tutti i valori.
            self._test_mode = True
            print("[RemoteResearcher] TEST_MODE abilitato.")
        else:
            # Imposta expected_value iniziale tramite il metodo autorizzato
            self.set_expected_value(0.33)
            print(f"[RemoteResearcher] Avvio con DATA='{self._input_data}' expected_value={self._current_expected_value}")
            
        #SE NON ESSITE UN COTNROLLO REMOTO MA TUTTI I PARAMETRI SONO IMPOSTATI GIA ALL'INIZIO
        # modificare le funzioni remote in modo che siano chiamate durante il ciclo di vita del gioco
        # ma con parametri predefiniti per ogni sessione


    def start_metrics(self) -> None:
        """Log SESSION_START e abilita le metriche con l'expected value corrente.

        In TEST_MODE usa il primo valore di CONVERTING_TABLE come placeholder;
        testing_statistics sovrascriverà expected_value spin per spin.
        """
        self._metrics_logger.log_session_start()
        if not self._test_mode:
            self._metrics_logger.enable_metrics(expected_value=self._current_expected_value)


    # ------------------------------------------------------------------
    # Aggiornamento expected value — UNICO punto autorizzato
    # ------------------------------------------------------------------

    def set_expected_value(self, expected_value: float) -> None:
        """Aggiorna WIN_PERCENTAGE in slot_logic e lo stato interno.

        UNICO metodo autorizzato a chiamare update_expected_value().

        Args:
            expected_value: Deve essere una chiave valida di CONVERTING_TABLE.

        Raises:
            ValueError: Se expected_value non è in CONVERTING_TABLE.
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
        """Stub: aggiorna expected_value da remoto (es. via TCP)."""
        self.set_expected_value(new_expected_value)  # passa dal metodo autorizzato
        self._metrics_logger.log_remote_change_expected_value(new_expected_value)

    def remote_charge_coin(self, amount: float, current_coins: float) -> None:
        """Stub: aggiunge coins da remoto (es. via TCP)."""
        self._metrics_logger.log_remote_charge_coin(amount=amount, coin_after=current_coins)

    def remote_send_message(self, message: str) -> None:
        """Stub: invia un messaggio da remoto (es. via TCP)."""
        self._metrics_logger.log_remote_message(message)