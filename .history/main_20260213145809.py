import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def load_stylesheet(x):
    with open("gui/styles/style.qss", "r") as f:
        x.setStyleSheet(f.read())

if __name__ == "__main__":
    app = QApplication()
    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
