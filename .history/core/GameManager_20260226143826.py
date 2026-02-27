'''creazione di una classe SINGLETON per la gestione del gioco,
contiene tutte la variabili globali accessibili da tutte le classe e i metodi 
per l'aggiornamento di tali variabili interne'''

class GameManager:
    _instance = None
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameManager, cls).__new__(cls)
            # Inizializza le variabili globali qui
            cls._instance.condition = None
            cls._instance.phase = None
            cls._instance.bet_counter = 0
        return cls._instance

    def update_condition(self, condition: str) -> None:
        '''Aggiorna la condizione del gioco'''
        self.condition = condition