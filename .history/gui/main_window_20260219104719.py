from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon, QDoubleValidator
from PyQt5.QtCore import Qt, QTimer, QSize
import random

from core.slot_logic import spin_reels, calculate_reward
from core.sound_manager import play_sfx, play_bgm
from core.redeem_logic import validate_redeem_code
from gui.redeem_dialog import RedeemDialog
from core.metrics_logger import MetricsLogger   # ← NEW
from utils.file_manager import get_path

# Constants
INITIAL_COINS = 10


class MainWindow(QWidget):
    def __init__(self, metrics_logger: MetricsLogger):
        """
        Initialize the Slot Machine main window.
        Sets up the GUI components including:
        - Window properties (title, icon, minimum size)
        - Game variables (coins, bet, spin mechanics)
        - Asset loading (symbol pixmaps)
        - UI elements (bet controls, coin display, reels, spin button)
        - Layout configuration with proper spacing
        - Timer for spin animation
        - Background music playback
        The window uses a vertical layout with:
        - Top section: bet controls (left), watermark (center), redeem button and coin label (right)
        - Middle section: three reels (centered)
        - Bottom section: spin button (centered)
        """
        super().__init__()
        
        # ===============================
        #          LOG SETUP
        # ===============================
        self._metrics = metrics_logger
        self._metrics.log_session_start()  # Log session start

        # ===============================
        #          WINDOW SETUP
        self.setWindowTitle("Slot Machine")
        self.setWindowIcon(QIcon(get_path("gui", "assets", "icons", "app_icon.ico")))
        self.setMinimumSize(600, 400)

        # ===============================
        #          GAME VARIABLES
        # ===============================
        self.coins = INITIAL_COINS
        self.current_bet = 0.00
        self.spin_cost = 5
        self.symbol_size = 400
        self.spin_timer = QTimer()
        self.spin_speed = 80
        self.roll_frames = 50
        self.current_frame = 0

        # ===============================
        #          LOAD ASSETS
        # ===============================
        self.symbols = {
            "banana":  QPixmap(get_path("gui", "assets", "icons", "banana.png")),
            "bar":     QPixmap(get_path("gui", "assets", "icons", "bar.png")),
            "bell":    QPixmap(get_path("gui", "assets", "icons", "bell.png")),
            "cherry":  QPixmap(get_path("gui", "assets", "icons", "cherry.png")),
            "diamond": QPixmap(get_path("gui", "assets", "icons", "diamond.png")),
            "grape":   QPixmap(get_path("gui", "assets", "icons", "grape.png")),
            "lemon":   QPixmap(get_path("gui", "assets", "icons", "lemon.png")),
            "seven":   QPixmap(get_path("gui", "assets", "icons", "seven.png")),
            "star":    QPixmap(get_path("gui", "assets", "icons", "star.png")),
        }

        # ===============================
        #           UI ELEMENTS
        # ===============================
        # Bet selection widget (left side)
        """self.bet_display = QLabel("0.00")
        #voglio poter isnerire a mano il valore da inserire nella bet display: inserisci la funzione
        self.bet_display.setObjectName("bet_display")
        self.bet_display.setAlignment(Qt.AlignCenter)
        self.bet_display.setMinimumWidth(300)
        self.bet_display.setMinimumHeight(100)
        self.bet_display.setStyleSheet("font-size: 40px; font-weight: 700; border: 2px solid #333; padding: 10px;")
        """
        self.bet_display = QLineEdit("0.00")
        self.bet_display.setObjectName("bet_display")
        self.bet_display.setAlignment(Qt.AlignCenter)
        self.bet_display.setMinimumWidth(300)
        self.bet_display.setMinimumHeight(100)
        self.bet_display.setStyleSheet("font-size: 40px; font-weight: 700; border: 2px solid #333; padding: 10px;")
        self.bet_display.editingFinished.connect(self.on_bet_manual_input)

        self.bet_up_btn = QPushButton("▲")
        # voglio poter tener pressato il pulsante per aumentare la puntata, quindi uso setAutoRepeat(True) e setAutoRepeatInterval(100) per farlo ripetere ogni 100ms
        self.bet_up_btn.setAutoRepeat(True)
        self.bet_up_btn.setAutoRepeatInterval(50)
        self.bet_up_btn.setObjectName("bet_up_btn")
        self.bet_up_btn.setStyleSheet("font-size: 50px;")
        self.bet_up_btn.clicked.connect(self.increase_bet)
        
        self.bet_down_btn = QPushButton("▼")
        # voglio poter tener pressato il pulsante per aumentare la puntata, quindi uso setAutoRepeat(True) e setAutoRepeatInterval(100) per farlo ripetere ogni 100ms
        self.bet_down_btn.setAutoRepeat(True)
        self.bet_down_btn.setAutoRepeatInterval(50)
        self.bet_down_btn.setObjectName("bet_down_btn")
        self.bet_down_btn.setStyleSheet("font-size: 50px;")
        self.bet_down_btn.clicked.connect(self.decrease_bet)
        
        # Coins display (right side)
        self.coin_label = QLabel("")
        self.coin_label.setObjectName("coin_label")
        self.coin_label.setMinimumWidth(200)
        #self.coin_label.setStyleSheet("font-size: 50px; font-weight: 700;") #nel CSS
        self.update_coin_label()

        self.redeem_btn = QPushButton("Redeem Coin")
        self.redeem_btn.setObjectName("redeem_btn")
        self.redeem_btn.clicked.connect(self.on_redeem)

        self.watermark = QLabel("UPV Slot Machine")
        # i need to make the Lable larger to fit the text, otherwise it will be cut off
        self.watermark.setAlignment(Qt.AlignCenter)
        self.watermark.setObjectName("watermark")
        #self.watermark.setStyleSheet("font-size: 50px; font-weight: 600;") #sostituisce il style del watermark, che prima era definito nel file css, ma ora è definito direttamente qui per evitare problemi di dimensioni del testo che veniva tagliato

        # Reels
        self.reel1 = QLabel()
        self.reel2 = QLabel()
        self.reel3 = QLabel()

        for reel in (self.reel1, self.reel2, self.reel3):
            reel.setObjectName("reel")
            reel.setAlignment(Qt.AlignCenter)
            reel.setPixmap(self.symbols["seven"].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
            reel.setMinimumSize(self.symbol_size, self.symbol_size)

        self.spin_btn = QPushButton("GIOCA")
        self.spin_btn.setObjectName("spin_btn")
        self.spin_btn.setEnabled(False)
        self.spin_btn.clicked.connect(self.on_spin)

        # ===============================
        #            LAYOUTS
        # ===============================
        # Bet widget layout (left side)
        bet_controls = QVBoxLayout()
        bet_controls.addWidget(self.bet_up_btn)
        bet_controls.addWidget(self.bet_display)
        bet_controls.addWidget(self.bet_down_btn)
        bet_controls.addStretch()
        
        # redeem + coins layout (right side)
        redeem_layout = QVBoxLayout()
        redeem_layout.addWidget(self.redeem_btn)
        redeem_layout.addWidget(self.coin_label)
        redeem_layout.addStretch()
        
        # Top layout: bet (left), watermark (center), redeem + coins (right)
        top = QHBoxLayout()
        top.addLayout(bet_controls)
        top.addStretch()
        top.addWidget(self.watermark)
        top.addStretch()
        top.addWidget(self.redeem_btn)
        top.addWidget(self.coin_label)

        # Middle layout: reels centered
        reels = QHBoxLayout()
        reels.addStretch()
        reels.addWidget(self.reel1)
        reels.addWidget(self.reel2)
        reels.addWidget(self.reel3)
        reels.addStretch()

        #inserimento in basso a sinistra del controllo audio (per ora solo un bottone per attivare/disattivare la musica, da vedere se è meglio mettere un toggle o un semplice bottone che cambia testo da "Music On" a "Music Off")
        '''self.music_btn = QPushButton("Music Off")
        self.music_btn.setObjectName("music_btn")
        self.music_btn.clicked.connect(self.toggle_music)
        music = QVBoxLayout()
        music.addWidget(self.music_btn)'''
        
        
        root = QVBoxLayout()
        root.addLayout(top)
        root.addStretch()
        root.addLayout(reels)
        root.addStretch()
        root.addWidget(self.spin_btn, alignment=Qt.AlignCenter)

        self.setLayout(root)

        # Timer animation
        self.spin_timer.timeout.connect(self.animate_spin)

        # ===============================
        #            START BGM
        # ===============================
        #play_bgm("bgm.mp3")







    def update_coin_label(self):
        self.coin_label.setText(f"🪙 {self.coins:.2f}")
    
    def update_bet_display(self):
        """Updates bet display and validates without triggering editingFinished"""
        self.bet_display.blockSignals(True)  # Prevent recursive calls
        self.bet_display.setText(f"{self.current_bet:.2f}")
        self.bet_display.blockSignals(False)
        self.validate_bet()
    
    def on_bet_manual_input(self):
        """Handles manual bet input from keyboard, rounds to nearest 0.10"""
        play_sfx("click.wav")
        # Get text and convert to float
        text = self.bet_display.text().strip().replace(",", ".")  # Handle comma as decimal
        
        # Validate input is not empty
        if not text:
            self.current_bet = 0.00
            self.update_bet_display()
            return
        
        try:
            value = float(text)
            # Ensure value is non-negative
            if value < 0:
                value = 0.00
        except ValueError:
            value = 0.00
        
        # Round to nearest 0.10
        self.current_bet = round(value / 0.10) * 0.10
        
        # Clamp to valid range
        self.current_bet = max(0.00, min(self.current_bet, self.coins))
        
        # Update display
        self.update_bet_display()
    
    def increase_bet(self):
        play_sfx("click.wav")
        self.current_bet = round(self.current_bet + 0.10, 2)
        self.update_bet_display()
    
    def decrease_bet(self):
        play_sfx("click.wav")
        if self.current_bet >= 0.10:
            self.current_bet = round(self.current_bet - 0.10, 2)
            self.update_bet_display()
    
    def validate_bet(self):
        """Enable GIOCA button only if bet is valid (> 0 and <= available coins)"""
        is_valid = self.current_bet > 0 and self.current_bet <= self.coins
        self.spin_btn.setEnabled(is_valid)

    def on_redeem(self):
        play_sfx("click.wav")
        dialog = RedeemDialog(redeem_callback=self.redeem_code_callback, parent=self)
        dialog.exec_()

    def on_spin(self):
        play_sfx("click.wav")

        self.watermark.setText("UPV Slot Machine")
        self.spin_btn.setDisabled(True)

        #OLD BET VALIDATION (before adding bet multiplier and cost)
        #if self.coins < self.spin_cost:
        #    self.watermark.setText("Not enough coins!")
        #    self.spin_btn.setDisabled(False)
        #    return

        if self.current_bet <= 0 or self.current_bet > self.coins:
            self.watermark.setText("Puntata non valida!")
            self.spin_btn.setDisabled(False)
            return

        play_sfx("spin.wav")
        
        # LOG BET before deducting coins
        self._metrics.log_bet(self.current_bet, coin_before=self.coins)
        
        #self.coins -= self.spin_cost # <- OLD
        self.coins -= self.current_bet
        self.update_coin_label()
        #spin_reels() -> ad esempio ("cherry", "cherry", "lemon")
        self.final_result = spin_reels() #restituisce una tupla di 3 simboli, ad esempio ("cherry", "cherry", "lemon")

        self.current_frame = 0
        self.spin_timer.start(self.spin_speed)

    def animate_spin(self):
        self.current_frame += 1

        random_symbols = list(self.symbols.values())

        self.reel1.setPixmap(random.choice(random_symbols).scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        self.reel2.setPixmap(random.choice(random_symbols).scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        self.reel3.setPixmap(random.choice(random_symbols).scaledToWidth(self.symbol_size, Qt.SmoothTransformation))

        if self.current_frame >= self.roll_frames:
            self.spin_timer.stop()
            self.show_final_result()
            self.spin_btn.setDisabled(False)

    def show_final_result(self):
        r1, r2, r3 = self.final_result #estraggo i simboli del risultato finale

        self.reel1.setPixmap(self.symbols[r1].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        self.reel2.setPixmap(self.symbols[r2].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        self.reel3.setPixmap(self.symbols[r3].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        # reward = calculate_reward([r1, r2, r3])
        # Calcolo ricompensa con moltiplicatore pari al valore della puntata 
        # Es. SEVEN (3: 100 ; 2: 10):se punto 0.20 e ottengo 3 SEVEN (premio 100) allora ottengo 20
        reward = calculate_reward([r1, r2, r3], self.current_bet)
        self.coins += reward
        self.update_coin_label()
        self.validate_bet()

        # LOG RESULT after coins are updated
        self._metrics.log_result(result_tuple=(r1,r2,r3), 
                                 reward=reward,
                                 coin_after=self.coins) #coins updated sopra

        if reward > 0:
            play_sfx("win.wav")
            self.watermark.setText(f"Hai vinto +{reward:.2f}")
        else:
            self.watermark.setText("Try again!")

    def redeem_code_callback(self, code: str) -> int:
        coins_to_add = validate_redeem_code(code)
        if coins_to_add:
            self.coins += coins_to_add
            self.update_coin_label()
            self.validate_bet()
            play_sfx("click.wav")
            return coins_to_add
        return 0


    # LOGGING METHODS (called from main_window and core logic)
    def closeEvent(self, event) -> None: 
        """Intercepts window close to log SESSION_END before exit."""
        self._metrics.log_session_end()
        super().closeEvent(event)