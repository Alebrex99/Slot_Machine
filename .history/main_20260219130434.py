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
    # RICERCATORE ESTERNO
    metrics_logger.enable_metrics(expected_value=0.33)  # Enable logging with desired expected value
    input_value = input("Press Enter to exit..")  # Keep the application running until user input
    print("Exiting application...", input_value)
    window = MainWindow(metrics_logger=metrics_logger)
    window.show()
 

    sys.exit(app.exec_())
