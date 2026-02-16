from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize
import random

from core.slot_logic import spin_reels, calculate_reward
from core.sound_manager import play_sfx, play_bgm
from core.redeem_logic import validate_redeem_code
from gui.redeem_dialog import RedeemDialog

from utils.file_manager import get_path

# Constants
INITIAL_COINS = 10


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

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
        self.bet_display = QLabel("0.00")
        self.bet_display.setObjectName("bet_display")
        self.bet_display.setAlignment(Qt.AlignCenter)
        self.bet_display.setMinimumWidth(300)
        self.bet_display.setMinimumHeight(100)
        self.bet_display.setStyleSheet("font-size: 40px; font-weight: 700; border: 2px solid #333; padding: 10px;")
        
        self.bet_up_btn = QPushButton("▲")
        self.bet_up_btn.setObjectName("bet_up_btn")
        self.bet_up_btn.clicked.connect(self.increase_bet)
        
        self.bet_down_btn = QPushButton("▼")
        self.bet_down_btn.setObjectName("bet_down_btn")
        self.bet_down_btn.clicked.connect(self.decrease_bet)
        
        # Coins display (right side)
        self.coin_label = QLabel("")
        self.coin_label.setObjectName("coin_label")
        self.coin_label.setMinimumWidth(200)
        self.coin_label.setStyleSheet("font-size: 30px; font-weight: 700;")
        self.update_coin_label()

        self.redeem_btn = QPushButton("Redeem Coin")
        self.redeem_btn.setObjectName("redeem_btn")
        self.redeem_btn.clicked.connect(self.on_redeem)

        self.watermark = QLabel("UPV Slot Machine")
        # i need to make the Lable larger to fit the text, otherwise it will be cut off
        self.watermark.setAlignment(Qt.AlignCenter)
        self.watermark.setObjectName("watermark")
        self.watermark.setStyleSheet("font-size: 50px; font-weight: 600;") #sostituisce il style del watermark, che prima era definito nel file css, ma ora è definito direttamente qui per evitare problemi di dimensioni del testo che veniva tagliato

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
        
        # Top layout: bet (left), watermark (center), redeem + coins (right)
        top = QHBoxLayout()
        top.addLayout(bet_controls)
        #top.addStretch()
        top.addWidget(self.watermark)
        top.addStretch()
        top.addWidget(self.redeem_btn)
        top.addWidget(self.coin_label)

        reels = QHBoxLayout()
        reels.addStretch()
        reels.addWidget(self.reel1)
        reels.addWidget(self.reel2)
        reels.addWidget(self.reel3)
        reels.addStretch()

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
        play_bgm("bgm.mp3")

    def update_coin_label(self):
        self.coin_label.setText(f"🪙 {self.coins:.2f}")
    
    def update_bet_display(self):
        self.bet_display.setText(f"{self.current_bet:.2f}")
        self.validate_bet()
    
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
        #self.coins -= self.spin_cost
        self.coins -= self.current_bet
        self.update_coin_label()

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
        r1, r2, r3 = self.final_result

        self.reel1.setPixmap(self.symbols[r1].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        self.reel2.setPixmap(self.symbols[r2].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        self.reel3.setPixmap(self.symbols[r3].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        # reward = calculate_reward([r1, r2, r3])
        reward = calculate_reward([r1, r2, r3], self.current_bet)
        self.coins += reward
        self.update_coin_label()
        self.validate_bet()

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
