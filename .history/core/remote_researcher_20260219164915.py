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


class RemoteResearcher:
    def __init__(self, metrics_logger):
        self._metrics_logger = metrics_logger
        self._current_expected_value = None
        self._input_data = None
        

    def set_input_data(self):
        '''Metodo per gestire l'input del ricercatore esterno. Può essere chiamato in qualsiasi momento per aggiornare i dati.'''
        self._input_data = input("Insert DATA: ")  # Keep the application running until user input
        input("Press ENTER to start application with DATA: " + self._input_data)  # Wait for user to press Enter again before starting the application
        print("Starting application... ", self._input_data)

    def start_metrics(self):
        # dopo che il ricercatore ha dato il via, avviene il logging iniziale e l'abilitazione metriche
        self._metrics_logger.log_session_start()  # Log session start
        self.set_expected_value(0.33)  # Set initial expected value (can be modified based on input)
        self._metrics_logger.enable_metrics(expected_value=self._current_expected_value)  # Enable logging with desired expected value

    def set_expected_value(self, expected_value):
        '''Metodo per aggiornare l'expected value durante il gioco, in base all'input del ricercatore.'''
        self._current_expected_value = expected_value

    def get_current_expected_value(self):
         return self._current_expected_value