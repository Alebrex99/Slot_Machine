import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.metrics_logger import MetricsLogger


def load_stylesheet(x):
    with open("gui/styles/style.qss", "r") as f:
        x.setStyleSheet(f.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app)

    metrics_logger = MetricsLogger()  # Initialize metrics logger (creates file if needed)
    
    # RICERCATORE ESTERNO: solo dopo aver inserito tutti i dati, da il via alla slot + logging
    input_value = input("Insert DATA: Press Enter to insert DATA..")  # Keep the application running until user input
    input("Press ENTER to start application with DATA: " + input_value)  # Wait for user to press Enter again before starting the application
    print("Exiting application...", input_value)
    
    # finito 
    metrics_logger.log_session_start()  # Log session start
    metrics_logger.enable_metrics(expected_value=0.33)  # Enable logging with desired expected value
    
    window = MainWindow(metrics_logger=metrics_logger)
    window.show()
 

    sys.exit(app.exec_())
