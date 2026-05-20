import sys
from PyQt5.QtWidgets import QApplication
from core.remote_researcher import RemoteResearcher
from gui.main_window import MainWindow
from core.metrics_logger import MetricsLogger
# from core.constants import BUILD_CONDITION # Variante
from utils.build_config import BUILD_CONDITION, IS_TEST_BUILD, MESSAGE_TYPE
from utils.file_manager import get_path

import os
from utils.file_manager import get_writable_path

# Write debug output to a log file (visible regardless of --windowed flag)
_debug_log = os.path.join(os.path.dirname(sys.executable), "app_debug.log")
with open(_debug_log, "w") as f:
    f.write(f"\n=== APPLICATION STARTUP ===\n")
    f.write(f"Executable: {sys.executable}\n")
    f.write(f"Executable dir: {os.path.dirname(sys.executable)}\n")
    f.write(f"Data path: {get_writable_path('data')}\n")
    f.write(f"BUILD_CONDITION: {BUILD_CONDITION}\n")
    f.write(f"IS_TEST_BUILD: {IS_TEST_BUILD}\n")
    f.write(f"MESSAGE_TYPE: {MESSAGE_TYPE}\n")
    f.write(f"=== END STARTUP ===\n")

print(f"\n=== APPLICATION STARTUP ===")
print(f"Executable: {sys.executable}")
print(f"Executable dir: {os.path.dirname(sys.executable)}")
print(f"Data path: {get_writable_path('data')}")
print(f"BUILD_CONDITION: {BUILD_CONDITION}")
print(f"IS_TEST_BUILD: {IS_TEST_BUILD}")
print(f"MESSAGE_TYPE: {MESSAGE_TYPE}")
print(f"Debug log written to: {_debug_log}")
print(f"=== END STARTUP ===\n")


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
    # metrics_logger = MetricsLogger(is_test_build=IS_TEST_BUILD) 
    # WITH TEST BUILD
    metrics_logger = MetricsLogger(is_test_build=IS_TEST_BUILD)  
    # REMOTE RESEARCHER: ha il compito di avviare app con i parametri
    remote_researcher = RemoteResearcher(metrics_logger=metrics_logger)  # Initialize remote researcher (waits for input)
    
    # BUILD_CONDITION: se non c'è allora si passa all'input, è fondamentale
    if BUILD_CONDITION is not None:
        # Fixed build: condition is baked in — skip interactive prompt
        remote_researcher.set_condition(BUILD_CONDITION)
        # remote_researcher.start_metrics()
        # WITH TEST BUILD
        if not IS_TEST_BUILD:
            remote_researcher.start_metrics()
    else:
        # Manual mode: existing interactive flow unchanged
        remote_researcher.set_input_data()
        # remote_researcher.start_metrics()
        # WITH TEST BUILD
        if not IS_TEST_BUILD:
            remote_researcher.start_metrics()  # in modalità normale, start_metrics viene chiamato dopo l'input
        


    
    window = MainWindow(metrics_logger=metrics_logger)
    window.show()

    # Se TEST_MODE è attivo, avvia il test automatico sincrono
    # La GUI rimane visibile ma disabilitata per tutta la durata del test.
    if remote_researcher.test_mode:
        #TODO ATTENZIONE: se si seleziona la v1 decommentare l'auto-close in _execute_spin_logic()
        #window.testing_statistics_v1()
        window.testing_statistics_v2(remote_researcher=remote_researcher)

    sys.exit(app.exec_())
