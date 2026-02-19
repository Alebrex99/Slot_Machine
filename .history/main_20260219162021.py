import sys
"""
Modulo principale dell'applicazione GUI.
Responsabilità:
- Crea l'istanza QApplication e applica il foglio di stile da "gui/styles/style.qss".
- Inizializza MetricsLogger (prepara/crea il file CSV per le metriche).
- Inizializza RemoteResearcher, attende l'input del ricercatore (set_input_data()) e avvia la sessione (start_session()) per registrare l'inizio e abilitare le metriche.
- Crea e mostra MainWindow passando l'istanza di MetricsLogger.
- Avvia il ciclo principale dell'app Qt (app.exec_()).
Effetti collaterali:
- Lettura del file di stile dal filesystem.
- Creazione/modifica del file CSV tramite MetricsLogger.
- Possibili operazioni di I/O o rete eseguite da RemoteResearcher.
Uso:
- Destinato ad essere eseguito come script principale (if __name__ == "__main__").
"""
"""
load_stylesheet(x)
Carica il file "gui/styles/style.qss" e applica il contenuto come stylesheet
all'oggetto Qt fornito.
Parametri:
- x: istanza di QApplication o QWidget che implementa setStyleSheet(str).
Comportamento:
- Apre il file "gui/styles/style.qss" in lettura e chiama x.setStyleSheet(contenuto).
Eccezioni:
- Propaga IOError/OSError se il file non è accessibile o non esiste.
"""
from PyQt5.QtWidgets import QApplication
from core.remote_researcher import RemoteResearcher
from gui.main_window import MainWindow
from core.metrics_logger import MetricsLogger


def load_stylesheet(x):
    with open("gui/styles/style.qss", "r") as f:
        x.setStyleSheet(f.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app)

    # ALL'AVVIO APP: viene creato metrics_logger, che prepara il file CSV (solo colonne) metriche
    metrics_logger = MetricsLogger()  # Initialize metrics logger (creates file if needed)
    
    # REMOTE RESEARCHER: ha il compito di avviare app con i parametri
    remote_researcher = RemoteResearcher(metrics_logger=metrics_logger)  # Initialize remote researcher (waits for input)
    remote_researcher.set_input_data()  # Wait for researcher input before proceeding
    remote_researcher.start_session()  # Log session start and enable metrics with expected value
    
    window = MainWindow(metrics_logger=metrics_logger)
    window.show()
 

    sys.exit(app.exec_())
