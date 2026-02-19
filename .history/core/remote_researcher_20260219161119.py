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

class RemoteResearcher:
    def __init__(self, metrics_logger, ):
        self._metrics_logger = metrics_logger
        self._current_expected_value = None
        self._input_value = None
        

    def set_input_data(self, input_value):
        '''Metodo per gestire l'input del ricercatore esterno. Può essere chiamato in qualsiasi momento per aggiornare i dati.'''
        input_value = input("Insert DATA: ")  # Keep the application running until user input
        input("Press ENTER to start application with DATA: " + input_value)  # Wait for user to press Enter again before starting the application
        print("Starting application... ", input_value)
        self._input_value = input_value

    def get_current_expected_value(self):
         return self._current_expected_value