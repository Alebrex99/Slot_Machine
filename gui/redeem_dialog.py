from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class RedeemDialog(QDialog):
    def __init__(self, redeem_callback, parent=None):
        """
        redeem_callback: function to call with code string, should return coins awarded
        """
        super().__init__(parent)
        self.setWindowTitle("Redeem Coin")

        self.redeem_callback = redeem_callback

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter your redeem code:"))
        self.input = QLineEdit()
        layout.addWidget(self.input)

        self.submit_btn = QPushButton("Redeem")
        self.submit_btn.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def on_submit(self):
        code = self.input.text().strip()
        if not code:
            QMessageBox.warning(self, "Error", "Please enter a code.")
            return

        coins = self.redeem_callback(code)
        if coins > 0:
            QMessageBox.information(self, "Success!", f"Redeem successful! You got {coins} 🪙")
            self.accept()
        else:
            QMessageBox.warning(self, "Invalid Code", "This redeem code is invalid or already used.")
