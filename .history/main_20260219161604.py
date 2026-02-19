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

    # ALL'AVVIO APP: viene creato metrics_logger per la preparazione del file CSV (solo colonne)
    metrics_logger = MetricsLogger()  # Initialize metrics logger (creates file if needed)
    
    remote_researcher = RemoteResearcher(metrics_logger=metrics_logger)  # Initialize remote researcher (waits for input)
    remote_researcher.set_input_data()  # Wait for researcher input before proceeding
    remote_researcher.start_session()  # Log session start and enable metrics with expected value
    
    
    
    window = MainWindow(metrics_logger=metrics_logger)
    window.show()
 

    sys.exit(app.exec_())
