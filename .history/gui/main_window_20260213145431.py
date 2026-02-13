from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize
import random

from core.slot_logic import spin_reels, calculate_reward
from core.sound_manager import play_sfx, play_bgm
from core.redeem_logic import validate_redeem_code
from gui.redeem_dialog import RedeemDialog

from utils.file_manager import get_path


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Slot Machine")
        self.setWindowIcon(QIcon(get_path("gui", "assets", "icons", "app_icon.ico")))
        self.setMinimumSize(600, 400)

        # ===============================
        #          GAME VARIABLES
        # ===============================
        self.coins = 100
        self.spin_cost = 5
        self.symbol_size = 130
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
        self.coin_label = QLabel("")
        self.coin_label.setObjectName("coin_label")
        self.update_coin_label()

        self.redeem_btn = QPushButton("Redeem Coin")
        self.redeem_btn.setObjectName("redeem_btn")
        self.redeem_btn.clicked.connect(self.on_redeem)

        self.watermark = QLabel("UPV Slot Machine")
        self.watermark.setAlignment(Qt.AlignCenter)
        self.watermark.setObjectName("watermark")

        # Reels
        self.reel1 = QLabel()
        self.reel2 = QLabel()
        self.reel3 = QLabel()

        for reel in (self.reel1, self.reel2, self.reel3):
            reel.setObjectName("reel")
            reel.setAlignment(Qt.AlignCenter)
            reel.setPixmap(self.symbols["seven"].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
            reel.setMinimumSize(self.symbol_size, self.symbol_size)

        self.spin_btn = QPushButton("SPIN")
        self.spin_btn.setObjectName("spin_btn")
        self.spin_btn.clicked.connect(self.on_spin)

        # ===============================
        #            LAYOUTS
        # ===============================
        top = QHBoxLayout()
        top.addWidget(self.coin_label)
        top.addWidget(self.redeem_btn)
        top.addStretch()
        top.addWidget(self.watermark)
        top.addStretch()

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
        self.coin_label.setText(f"🪙 {self.coins}")

    def on_redeem(self):
        play_sfx("click.wav")
        dialog = RedeemDialog(redeem_callback=self.redeem_code_callback, parent=self)
        dialog.exec_()

    def on_spin(self):
        play_sfx("click.wav")

        self.watermark.setText("UPV Slot Machine")
        self.spin_btn.setDisabled(True)

        if self.coins < self.spin_cost:
            self.watermark.setText("Not enough coins!")
            self.spin_btn.setDisabled(False)
            return

        play_sfx("spin.wav")

        self.coins -= self.spin_cost
        self.update_coin_label()

        self.final_result = spin_reels()

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

        reward = calculate_reward([r1, r2, r3])
        self.coins += reward
        self.update_coin_label()

        if reward > 0:
            play_sfx("win.wav")
            self.watermark.setText(f"WIN +{reward} 🪙")
        else:
            self.watermark.setText("Try again!")

    def redeem_code_callback(self, code: str) -> int:
        coins_to_add = validate_redeem_code(code)
        if coins_to_add:
            self.coins += coins_to_add
            self.update_coin_label()
            play_sfx("click.wav")
            return coins_to_add
        return 0
