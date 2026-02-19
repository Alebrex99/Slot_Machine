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
    '''# RICERCATORE ESTERNO: solo dopo aver inserito tutti i dati, da il via alla slot + logging
    # Possiamo costruire una classe a parte per gestire: input, log ricercatore, abilitazione metriche, e poi passare il logger alla main window. Per ora lo facciamo direttamente in main.py
    input_value = input("Insert DATA: ")  # Keep the application running until user input
    input("Press ENTER to start application with DATA: " + input_value)  # Wait for user to press Enter again before starting the application
    print("Starting application... ", input_value)'''
    
    
    window = MainWindow(metrics_logger=metrics_logger)
    window.show()
 

    sys.exit(app.exec_())
