'''VARIANTE CON BOTTOM COINTER SOTTO IMMAGINE'''


from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt
from utils.file_manager import get_path
from core.constants import MESSAGE_TIMER, MESSAGE_TYPE

# How many seconds before end the MEX2 countdown becomes visible.
_COUNTDOWN_START = 10


# OLD: class MessageWindow(QDialog):

# COSA E' MessageWindow + parent = self.overlay = QWidget(self) in MainWindow
# è esattamente un Qwidget che avrei potuto creare anche in MainWindow perchè è figlio di QWidget + usa parent
# se fosse solo figlio di Qwidget senza parent sarebbe una finestra OS separata
class MessageWindow(QWidget): # con QWidget + uso del parent tale ifnestra è solamente figlia della MainWindow, non una finestra OS separata e riadattata
    """Full-screen overlay shown between bet 40 and bet 41.

    Implemented as a child QWidget of MainWindow so it covers the client area
    (content below the title bar) but leaves the OS MainWindow title bar free.
    This lets the user move, resize, and close the main window while the overlay
    is visible — which was impossible with the previous QDialog + ApplicationModal approach.

        - Covers the parent's client area (geometry 0,0,w,h — NOT frameGeometry).
        - Loads mex1.png (MEX1) or mex2.png (MEX2) from gui/assets/icons/.
          Falls back to banana.png if the file is missing.
        - 30-second timer; CLOSE button (300 px wide, centered) disabled until it expires.
        - MEX2 only: numeric countdown appears next to CLOSE during the last 10 s.
        - Programmatic close() is blocked before the timer expires.
        - open_message_callback() is fired exactly once on close.
        - MainWindow.resizeEvent() calls _sync_to_parent() to keep the overlay sized.
    """

    def __init__(self, open_message_callback, parent=None):
        super().__init__(parent) # X COPRIRE CONTROLLI APP -> METTERE NONE
        # self.main_window = parent # X COPRIRE CONTROLLI APP, MA NON SI PUO RIDIMENSIONARE LA FINESTRA
        self.open_message_callback = open_message_callback
        self._timer_done = False
        self._callback_fired = False  # garantisce esecuzione una tantum del callback

        # VERSIONE MessageWindow(QDialog)
        # OLD: setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # Settare tipo di finestra: senza pulsanti e barra di stato (FramelessWindowHint) e sempre in primo piano, cioè se utente clicca altrove il mex è in overlay (WindowStaysOnTopHint) 
        # OLD: setWindowModality(Qt.ApplicationModal) # blocca interazioni con la main window, ma anche con la title bar (move/resize/close) — non va bene per un child QWidget; # non Qt.WindowModal perchè blocco percorsi alternativi per far avanzare il gioco
        # → rimossi: non servono per un child QWidget; ApplicationModal bloccava anche
        #   il title bar della main window impedendo move/resize/close.

   
        #if self.main_window: # X COPRIRE CONTROLLI APP, MA NON SI PUO RIDIMENSIONARE LA FINESTRA
        if parent:
            self.setGeometry(0, 0, parent.width(), parent.height()) # Usando invece: self.setGeometry(self.main_window.frameGeometry())  ← coordinate globali, copriva anche il title bar
            # self.setGeometry(self.main_window.frameGeometry()) # X COPRIRE CONTROLLI APP, MA NON SI PUO RIDIMENSIONARE LA FINESTRA
            
        # Load and store original pixmap (re-scaled on every resize)
        img_file = "mex1.png" if MESSAGE_TYPE == "MEX1" else "mex2.png"
        self._pixmap = QPixmap(get_path("gui", "assets", "icons", img_file))
        if self._pixmap.isNull():
            self._pixmap = QPixmap(get_path("gui", "assets", "icons", "banana.png"))

        # ---------------Layout---------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Image fills all available vertical space (stretch=1).
        self.mex_label = QLabel()
        self.mex_label.setObjectName("mex_label")
        self.mex_label.setAlignment(Qt.AlignCenter)
        self.mex_label.setStyleSheet("background-color: black;")
        layout.addWidget(self.mex_label, 1)

        # Bottom row: [countdown]  [CLOSE]  - horizontally centered.
        # OLD: layout.addLayout(bottom) con QHBoxLayout → usa in realtà il global QWidget { background } del QSS
        #      applicava il colore grigio della MainWindow a solo il bottom della window secondaria (nera da mex_label)
        self.bottom_container = QWidget()
        self.bottom_container.setStyleSheet("background-color: black;")
        
        bottom = QHBoxLayout(self.bottom_container)
        bottom.setContentsMargins(0, 10, 0, 20)
        bottom.setSpacing(20)

        self.countdown_label = QLabel("")
        self.countdown_label.setObjectName("countdown_label")
        self.countdown_label.setAlignment(Qt.AlignCenter)

        self.close_btn = QPushButton("CLOSE")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.on_close)

        # bottom.addStretch(1) # causa la presenza della fascia grigia lungo tutta la finestra
        bottom.addWidget(self.countdown_label)
        bottom.addWidget(self.close_btn)
        # bottom.addStretch(1)
        layout.addWidget(self.bottom_container, 0, Qt.AlignHCenter)  # OLD: layout.addLayout(bottom)
        # --------------------------------------------------------------------------------

        # START
        self.bottom_container.setVisible(False)
        self._render_image()
        # Start the 30-second countdown
        self._elapsed = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)


    def _sync_to_parent(self):
        """Resize the overlay to fill the current parent client area."""
        p = self.parent()
        if p and self.isVisible():
            # Appena chiamato setGeometry -> Qt chiama resizeEvent() -> schedula _render_image() al prossimo loop
            self.setGeometry(0, 0, p.width(), p.height()) # spostamento in alto a sx + resize
            #self.setGeometry(self.main_window.frameGeometry()) # SE SI VUOLE COPRIRE CONTROLLI APP, MA NON SI PUO RIDIMENSIONARE LA FINESTRA
            self.raise_()  # rimane sopra i widget fratelli dopo il resize (per sicurezza, ma non serve)
            QTimer.singleShot(0, self._render_image)


    def _render_image(self):
        w = self.mex_label.width()
        h = self.mex_label.height()
        if w > 0 and h > 0 and not self._pixmap.isNull():
            self.mex_label.setPixmap(
                self._pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )


    def _tick(self):
        # Guard: if the dialog's C++ widgets were already destroyed (race with close),
        # stop the timer to prevent RuntimeError on the next tick.
        try: 
            _ = self.countdown_label.isVisible() # test if countdown_label exists (it should, but just in case)
        except RuntimeError:
            self._timer.stop()
            return
        
        self._elapsed += 1
        remaining = MESSAGE_TIMER - self._elapsed

        if MESSAGE_TYPE == "MEX2" and remaining <= _COUNTDOWN_START:
            self.bottom_container.setVisible(True)
            self.countdown_label.setText(str(max(remaining, 0)))

        if self._elapsed >= MESSAGE_TIMER:
            self._timer.stop()
            self._timer_done = True
            self.bottom_container.raise_() # tra fratelli
            self.close_btn.setEnabled(True)
            self.close_btn.setStyleSheet("background-color: green")


    def on_close(self):
        """Called by the CLOSE button after the timer expires."""
        self._timer.stop()
        if not self._callback_fired:
            self._callback_fired = True
            self.open_message_callback()
        # OLD: self.accept()  ← metodo QDialog; QWidget usa hide()
        self.hide()

    def closeEvent(self, event):
        """Blocca close() programmatico prima che il timer scada."""
        if not self._timer_done:
            event.ignore()
            return
        self._timer.stop()
        if not self._callback_fired:
            self._callback_fired = True
            self.open_message_callback()
        super().closeEvent(event)



    # FLUSSO: RESO PIU SEMPLICE COME update_reels()
    # resize MainWindow -> if message is visible -> sync_to_parent() -> setGeometry() causa 
    # -> resizeEvent() -> _render_image() -> rescale pixmap alla nuova dimensione
    '''def resizeEvent(self, event):
        print(f"Resize event: {event}")
        super().resizeEvent(event)
        # self._render_image() # funzione uguale ma con più flicker perchè si aggiornano tutti i px
        QTimer.singleShot(0, self._render_image)'''