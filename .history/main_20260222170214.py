import sys
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
    remote_researcher.set_input_data()  # Wait for researcher input before proceeding: imposta expected_value e test_mode in base a input DATA
    remote_researcher.start_metrics()  # Log session start and enable metrics with expected value corrente
     # se TEST_MODE testing_statistics fa sia enable_metrics per abilitare metriche, sia set_expected_value per iterare su tutti i valori di CONVERTING_TABLE durante il test automatico
    # se non TEST_MODE, l'expected_value è settato in input data e enable_metrics è chiamato dal researcher
    
    window = MainWindow(metrics_logger=metrics_logger)
    window.show()

    # Se TEST_MODE è attivo, avvia il test automatico sincrono.
    # La GUI rimane visibile ma disabilitata per tutta la durata del test.
    if remote_researcher.test_mode:
        window.testing_statistics(researcher=remote_researcher)

    sys.exit(app.exec_())
