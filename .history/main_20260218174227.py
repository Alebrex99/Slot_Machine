import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
import core.metrics as metrics


def load_stylesheet(app: QApplication) -> None:
    with open("gui/styles/style.qss", "r") as f:
        app.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app)

    # Log session start before showing the window
    metrics.log_session_start()

    window = MainWindow()
    window.show()

    exit_code = app.exec_()

    # Log session end after the event loop exits (window already closed)
    metrics.log_session_end()

    sys.exit(exit_code)
