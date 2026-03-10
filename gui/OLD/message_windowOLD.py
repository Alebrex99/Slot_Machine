from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt
from utils.file_manager import get_path
from core.constants import MESSAGE_TIMER, MESSAGE_TYPE

# How many seconds before end the MEX2 countdown becomes visible.
_COUNTDOWN_START = 10


# TODO probabilmente da rimpiazzare QDialog creando una finestra persistente (https://www.pythonguis.com/tutorials/creating-multiple-windows/)
class MessageWindow(QDialog):
    def __init__(self, open_message_callback, parent=None):
        """Full-screen modal overlay shown between bet 40 and bet 41.
            - Covers the parent window (frameless, application-modal).
            - Loads mex1.png (MEX1) or mex2.png (MEX2) from gui/assets/icons/.
            Falls back to banana.png if the file is missing.
            - 30-second timer; CLOSE button disabled until it expires.
            - MEX2 only: numeric countdown appears during the last 10 seconds.
            - Alt+F4 and programmatic close() are blocked before the timer expires.
            - open_message_callback() is fired exactly once on close.
        """

        super().__init__(parent)
        #self.setWindowTitle("Message Window")
        self.open_message_callback = open_message_callback
        
        
        # NEW -------------------
        self._timer_done = False
        self._callback_fired = False #serve per garantire esecuzione una tantum, in caso qualcuno chiami close() programmaticamente
        
        # ── Window flags: frameless + always on top + application-modal ──
        # Settare tipo di finestra: senza pulsanti e barra di stato (FramelessWindowHint) e sempre in primo piano, cioè se utente clicca altrove il mex è in overlay (WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) 
        # Rendi la window messaggio modale rispetto all'app, ovvero blocca interazioni con la main window
        self.setWindowModality(Qt.ApplicationModal) # non Qt.WindowModal perchè blocco percorsi alternativi per far avanzare il gioco,
        if parent:
            self.setGeometry(parent.geometry())  # cover the parent exactly
        # --------------------------
        
        # MESSAGE LAYOUT
        layout = QVBoxLayout()
        '''# OLD-------------------------------      
        # MESSAGE
        # Prova con immagine banana, da sostituire con il messaggio vero e proprio. Per ora è solo un placeholder per testare la logica di apertura del messaggio a bet 40, con timer di 30 secondi e chiusura al termine del timer.
        layout.setAlignment(Qt.AlignCenter)
        Mex_img = {"banana": QPixmap(get_path("gui", "assets", "icons", "banana.png"))}
        mex_label = QLabel()
        mex_label.setObjectName("mex_label")
        mex_label.setAlignment(Qt.AlignCenter)
        parent_width = self.parent().width() if self.parent() else 400
        parent_height = self.parent().height() if self.parent() else 300
        mex_label.setPixmap(Mex_img["banana"].scaled(parent_width, parent_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)) #sovrapponi esattamente la finstra, non mantenere le proporzioni, devi coincidere (altrimenti usa Qt.KeepAspectRatio)
        layout.addWidget(mex_label)

        # TIMER
        #impostare un timer che va a ritroso da 30 a 0, aggiornando il testo del timer_label ogni secondo
        self.timer_label = QLabel("Time remaining: 30s")
        self.timer = QTimer()
        self.timer_speed = 1000 #ms, ovvero 1 secondo
        self.timer_seconds = 30 # total seconds
        self.current_frame = 0
        layout.addWidget(self.timer_label)
        #allo start (spin_timer.start(self.spin_speed)) viene avviato un timer che ogni timer_speed ms (1000 ms) chiama la funzione update_timer.
        #ogni frame_speeds (1000 ms = 1s) viene richiamato il signal (update_timer, la funzione costantemente reinvocata).
        #Tempo totale animazione = timer_speed * roll_frames = 1000ms * 30 = 3000 ms
        #FPS = 1000ms / timer_speed = 1 FPS
        self.timer.timeout.connect(self.update_timer)
        
        # CLOSE BUTTON
        # il pusante CLOSE deve essere visualizzato e abilitato solo alla fine del TIMER
        self.close_btn = QPushButton("CLOSE")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.on_close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        
        # START TIMER
        print("START TIMER")
        self.timer.start(self.timer_speed)  # Update every second
        # ----------------------------------------------
        '''
        
        # NEW ------------------------------------------------
        layout.setContentsMargins(0, 0, 0, 0) # togli i margini di default al QBoxLayout
        layout.setSpacing(0)
     

        # ── Message image ─────────────────────────────────────────────────
        # Replace mex1.png / mex2.png in gui/assets/icons/ to change the image.
        img_file = "mex1.png" if MESSAGE_TYPE == "MEX1" else "mex2.png"
        pixmap = QPixmap(get_path("gui", "assets", "icons", img_file))
        if pixmap.isNull():  # fallback while real assets are not yet present
            pixmap = QPixmap(get_path("gui", "assets", "icons", "banana.png"))

        w = parent.width() if parent else 800
        h = parent.height() if parent else 600
        self.mex_label = QLabel()
        self.mex_label.setObjectName("mex_label")
        self.mex_label.setAlignment(Qt.AlignCenter)
        self.mex_label.setStyleSheet("background-color: black;")
        self.mex_label.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(self.mex_label, 1)  # stretch=1 → fills available space

        # ── Countdown label (MEX2 only, hidden until last 10 s) ───────────
        self.countdown_label = QLabel("")
        self.countdown_label.setObjectName("countdown_label")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet(
            "font-size: 80px; font-weight: bold; color: white;"
            "background-color: rgba(0,0,0,180); padding: 10px;"
        )
        self.countdown_label.setVisible(False)
        layout.addWidget(self.countdown_label)
        
        # ── Close button (disabled until timer expires) ───────────────────
        self.close_btn = QPushButton("CLOSE")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.on_close)
        layout.addWidget(self.close_btn)
        
        # ── Start the 30-second timer ─────────────────────────────────────
        self._elapsed = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)  # fires every second
        # ----------------------------------------------
        

    def _tick(self):
        self._elapsed += 1
        remaining = MESSAGE_TIMER - self._elapsed

        # MEX2: show large countdown during the last _COUNTDOWN_START seconds.
        if MESSAGE_TYPE == "MEX2" and remaining <= _COUNTDOWN_START:
            self.countdown_label.setVisible(True)
            self.countdown_label.setText(str(max(remaining, 0)))

        if self._elapsed >= MESSAGE_TIMER:
            self._timer.stop()
            self._timer_done = True
            self.countdown_label.setVisible(False)
            self.close_btn.setEnabled(True)
  

    def on_close(self):
        """Called by the CLOSE button after the timer expires."""
        print("MESSAGE CLOSED")
        print("Callback: reconnect on_spin()")
        self._timer.stop()
        if not self._callback_fired:
            self._callback_fired = True
            self.open_message_callback()
        self.accept() # internamente triggera closeEvent
        # allo stesso tempo se qualcuno chiama close() programmaticamente, anch'esso chiama CloseEvent


    # Chiamato internamente da on_close()
    # Metodo di QT: chiamato quando qualcosa tenta di chiudere la finestra, es. ALT+F4 o pulsante X se visibile
    def closeEvent(self, event): #Qt passa all'handler oggetto event
        """Override closeEvent to block Alt+F4 or programmatic close before timer expires."""
        """Blocks Alt+F4 and programmatic close() before the timer expires."""
        
        # Blocco tutto finchè non scade timer
        if not self._timer_done:
            event.ignore() # event.accept() è di default
            return
        
        # Quando timer scaduto
        self._timer.stop()
        if not self._callback_fired:
            self._callback_fired = True
            self.open_message_callback()
        super().closeEvent(event)







    # OLD METHODS ---------------------------------------------------------------------------------------------------------------
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