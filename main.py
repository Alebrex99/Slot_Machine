import sys
from PyQt5.QtWidgets import QApplication
from core.remote_researcher import RemoteResearcher
from gui.main_window import MainWindow
from core.metrics_logger import MetricsLogger
# from core.constants import BUILD_CONDITION # Variante
from utils.build_config import BUILD_CONDITION
from utils.file_manager import get_path

def load_stylesheet(x):
    # OLD senza build
    #with open("gui/styles/style.qss", "r") as f:
    #    x.setStyleSheet(f.read())
    
    # get_path() resolves correctly both in dev and in the frozen exe
    # (open("gui/styles/style.qss") breaks in .exe — CWD is not the project root)
    with open(get_path("gui", "styles", "style.qss"), "r") as f:
        x.setStyleSheet(f.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app)

    # ALL'AVVIO APP: viene creato metrics_logger, che prepara il file CSV (solo colonne) metriche
    metrics_logger = MetricsLogger()  # Initialize metrics logger (creates file if needed)
    # REMOTE RESEARCHER: ha il compito di avviare app con i parametri
    remote_researcher = RemoteResearcher(metrics_logger=metrics_logger)  # Initialize remote researcher (waits for input)
    
    if BUILD_CONDITION is not None:
        # Fixed build: condition is baked in — skip interactive prompt
        remote_researcher.set_condition(BUILD_CONDITION)
        remote_researcher.start_metrics()
    else:
        # Manual mode: existing interactive flow unchanged
        remote_researcher.set_input_data()
        remote_researcher.start_metrics()

    
    window = MainWindow(metrics_logger=metrics_logger)
    window.show()

    # Se TEST_MODE è attivo, avvia il test automatico sincrono
    # La GUI rimane visibile ma disabilitata per tutta la durata del test.
    if remote_researcher.test_mode:
        #TODO ATTENZIONE: se si seleziona la v1 decommentare l'auto-close in _execute_spin_logic()
        #window.testing_statistics_v1()
        window.testing_statistics_v2(remote_researcher=remote_researcher)

    sys.exit(app.exec_())
