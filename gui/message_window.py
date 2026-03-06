from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt
from utils.file_manager import get_path

# TODO probabilmente da rimpiazzare QDialog creando una finestra persistente (https://www.pythonguis.com/tutorials/creating-multiple-windows/)
class MessageWindow(QDialog):
    def __init__(self, open_message_callback, parent=None):
        """
        open_message_callback: function to call when the message is closed
        """
        super().__init__(parent)
        self.setWindowTitle("Message Window")
        self.open_message_callback = open_message_callback


        # MESSAGE LAYOUT
        layout = QVBoxLayout()
        
        # MESSAGE
        # Prova con immagine banana, da sostituire con il messaggio vero e proprio. Per ora è solo un placeholder per testare la logica di apertura del messaggio a bet 40, con timer di 30 secondi e chiusura al termine del timer.
        layout.setAlignment(Qt.AlignCenter)
        Mex_img = {"banana": QPixmap(get_path("gui", "assets", "icons", "banana.png"))}
        mex_label = QLabel()
        mex_label.setObjectName("mex_label")
        mex_label.setAlignment(Qt.AlignCenter)
        parent_width = self.parent().width() if self.parent() else 400
        parent_height = self.parent().height() if self.parent() else 300
        mex_label.setPixmap(Mex_img["banana"].scaled(parent_width, parent_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(mex_label)

        # TIMER
        #impostare un timer che va a ritroso da 30 a 0, aggiornando il testo del timer_label ogni secondo
        self.timer_label = QLabel("Time remaining: 30s")
        self.timer = QTimer()
        self.timer_speed = 1000 #ms, ovvero 1 secondo
        self.timer_seconds = 30 # total seconds
        self.current_frame = 0
        layout.addWidget(self.timer_label)
        '''allo start (spin_timer.start(self.spin_speed)) viene avviato un timer che ogni timer_speed ms (1000 ms) chiama la funzione update_timer.
        ogni frame_speeds (1000 ms = 1s) viene richiamato il signal (update_timer, la funzione costantemente reinvocata).
        Tempo totale animazione = timer_speed * roll_frames = 1000ms * 30 = 3000 ms
        FPS = 1000ms / timer_speed = 1 FPS'''
        self.timer.timeout.connect(self.update_timer)
 

        # CLOSE BUTTON
        # il pusante CLOSE deve essere visualizzato e abilitato solo alla fine del TIMER
        self.close_btn = QPushButton("CLOSE")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.on_close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        
        # START TIMER
        print("START TIMER")
        self.timer.start(self.timer_speed)  # Update every second

    def on_close(self):
        print("MESSAGE CLOSED")
        print("Callback: reconnect on_spin()")
        self.open_message_callback()
        self.accept()  # Close the dialog

    def enable_close_button(self):
        is_valid = True  # Replace with actual validation logic
        self.close_btn.setEnabled(is_valid)

    
    def update_timer(self):
        self.current_frame += 1
        # AGGIORNAMENTO VISIVO TIMER
        # Cosa succede aggiornado il timer ogni secondo? semplicemente viene mostrato il nuovo tempo a ritrso
        remaining_time = self.timer_seconds - self.current_frame
        self.timer_label.setText(f"Time remaining: {remaining_time}s")
    
        # FINE TIMER
        # permette all'utente di chiudere il messaggio
        if self.current_frame >= self.timer_seconds:
            self.timer.stop()
            self.enable_close_button()
        





    #OLD
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
