import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.metrics_logger import MetricsLogger

'''qua sopra ci sarà il server socket IO che riceverà
i dati direttamente dall'applicazione esterna (client) del ricercatore
farò una classe che si occupa di prelevare i dati e passarli successivamente sia alla MainWindow che
al MetricsLogger, in modo che possano essere visualizzati e salvati rispettivamente (da vedere per bene...)'''


def load_stylesheet(x):
    with open("gui/styles/style.qss", "r") as f:
        x.setStyleSheet(f.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app)

    metrics_logger = MetricsLogger()  # Initialize metrics logger (creates file if needed)
    metrics_logger.enable_metrics(expected_value=0.33)  # Enable logging with desired expected value
    # test an input to print a message on CLi
    input_value = input("Press Enter to exit..")  # Keep the application running until user input
    print("Exiting application...", input_value)
    window = MainWindow(metrics_logger=metrics_logger)
    window.show()
 

    sys.exit(app.exec_())
