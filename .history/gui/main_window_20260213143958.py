# Nella sezione "# Reels", modifica il loop:
for reel in (self.reel1, self.reel2, self.reel3):
    reel.setObjectName("reel")
    reel.setAlignment(Qt.AlignCenter)
    reel.setPixmap(self.symbols["seven"].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
    reel.setMinimumSize(self.symbol_size, self.symbol_size)
    reel.setScaledContents(True)  # Aggiungi questa linea

# Nel layout dei reel, modifica:
reels = QHBoxLayout()
reels.addStretch()
reels.addWidget(self.reel1)
reels.addWidget(self.reel2)
reels.addWidget(self.reel3)
reels.addStretch()

# Nel root layout, aumenta lo stretch:
root = QVBoxLayout()
root.addLayout(top)
root.addStretch(2)  # Cambia da addStretch() a addStretch(2)
root.addLayout(reels)
root.addStretch(2)  # Cambia da addStretch() a addStretch(2)
root.addWidget(self.spin_btn, alignment=Qt.AlignCenter)
