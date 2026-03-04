from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon, QDoubleValidator
from PyQt5.QtCore import Qt, QTimer, QSize
import random
import sys

from core.slot_logic import spin_reels, calculate_reward
from core.sound_manager import play_sfx, play_bgm
from core.redeem_logic import validate_redeem_code
from gui.redeem_dialog import RedeemDialog
from core.metrics_logger import MetricsLogger   # ← NEW
from utils.file_manager import get_path
from PyQt5.QtWidgets import QApplication
from core.constants import INITIAL_BUDGET, MIN_BET, MAX_BET, BET_STEP, TOTAL_SESSION_BETS, PHASE_LENGTH
 

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

        # ===============================
        #          WINDOW SETUP
        self.setWindowTitle("Slot Machine")
        self.setWindowIcon(QIcon(get_path("gui", "assets", "icons", "app_icon.ico")))
        self.setMinimumSize(600, 400)

        # ===============================
        #          GAME VARIABLES
        # ===============================
        self.coins = INITIAL_BUDGET
        self.current_bet = 0.00
        # Experimental session tracking
        self.bet_counter = 0  # counts from 0 -> increment before each bet to 1..60
        self.current_reward = 0.00
        
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

        # MUSIC CONTROLS
        self.music_btn = QPushButton("Music Off")
        self.music_btn.setObjectName("music_btn")
        self.music_btn.clicked.connect(self.toggle_music)

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
        music = QVBoxLayout()
        music.addWidget(self.music_btn)
        
        
        root = QVBoxLayout()
        root.addLayout(top)
        root.addStretch()
        root.addLayout(reels)
        root.addStretch()
        root.addWidget(self.spin_btn, alignment=Qt.AlignCenter)

        self.setLayout(root)

        # Timer animation
        '''
        allo start (spin_timer.start(self.spin_speed)) viene avviato un timer che ogni spin_speed ms (80 ms) chiama la funzione animate_spin.
        ogni frame_speeds (80 ms) viene richiamato il signal (animate_spin, la funzione costantemente reinvocata).
        Tempo totale animazione = spin_speed * roll_frames = 80ms * 50 = 4000ms = 4 secondi
        FPS = 1000ms / spin_speed = 1000ms / 80ms = 12.5 FPS'''
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
            # If value is above MAX_BET, clamp it
            if value > MAX_BET:
                value = MAX_BET
        except ValueError:
            value = 0.00
        
        # value needs to follow 0.10 steps, so we round it to nearest 0.10
        # Round to nearest 0.10. es. 2.3 -> 2.33/0.10 = 23.3 -> round(23.3) = 23 -> 23*0.10 = 2.30
        self.current_bet = round(value / BET_STEP) * BET_STEP
        
        # Update display
        self.update_bet_display()
    
    def increase_bet(self):
        play_sfx("click.wav")
        new_value = self.current_bet + BET_STEP
        if new_value > MAX_BET:
            self.current_bet = MAX_BET
        else:
            self.current_bet = round(self.current_bet + BET_STEP, 2)
        self.update_bet_display()
    
    def decrease_bet(self):
        play_sfx("click.wav")
        new_value = self.current_bet - BET_STEP
        if new_value >= 0:
            self.current_bet = round(self.current_bet - BET_STEP, 2)
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
        '''Logica di gioco quando si preme il pulsante GIOCA:
        - incremento il contatore di puntata, la prima puntata parte da 1, in quanto si calcola dal click sul game
        - verifica che il numero della puntata sia valido
        - verifica che il valore della scommessa inserita sia valido (non negativo e non superiore alla disponbilità di monete)
        - salvo il budget prima dello spin (budget_before_spin = self.coins)
        - calcolo la ricompensa che segue l'equazione: REWARD = BUDGET_INIZIALE_FASE (initial_budget) - BUDGET_BEFORE_SPIN (prima dello spin) + PUNTATA (current_bet)
        - eseguo effettivamente lo spin truccato e calcolo il corrispondente risultato alla reward, sapendo a priori la reward
        - aggiorno i coin correnti togliendo la puntata 
        ''' 
        
        # increment bet counter for this play: indica la bet corrente, non indica la successiva
        self.bet_counter += 1 # bet n 15: dopo l'incremento siamo alla bet corrente
        
        # è molto importante che quando l'app si chiude, alla successiva sessione le metriche vengano appese nel file
        # REVIEW NOTE: check moved to show_final_result AFTER bet 60 is fully processed and logged.
        # The old check here (> TOTAL_SESSION_BETS) would require a 61st press to trigger close,
        # leaving bet 60 processed but close only triggered on the next (61st) click.
        # if self.bet_counter > TOTAL_SESSION_BETS:
        #     self.close()
        #     return
        
        play_sfx("click.wav")

        self.watermark.setText("UPV Slot Machine")
        self.spin_btn.setDisabled(True)
        
        if self.current_bet <= 0 or self.current_bet > self.coins:
            self.watermark.setText("Puntata non valida!")
            self.spin_btn.setDisabled(False)
            return

        play_sfx("spin.wav")
        
        # LOGICA DI GIOCO: 
        # prima si calcola la REWARD, poi tramite quella si pesca nella REWARD_TABLE il simbolo + le occorrenze.
        budget_before_spin = self.coins #97.2
        # Visualizzo real-time i coin: deduct bet from coins (we'll log result after reward is applied)
        self.coins -= self.current_bet #97.2 - 0.2 = 97.0
        self.update_coin_label() # mostro 97.0
        
        # cosa fa calculate_reward (esempio):
        # expected_reward = 100 - 97.2 + 0.2 = 3.0
        # multiplier = 15x = reward / bet = 3.0 / 0.2 = 15
        # symbol = "lemon" , occurrence = 3
        # reward (gain_visualizzato, e reale per noi) = bet * multiplier = 0.2 * 15 = 3.0; attenzione bet già dedotta
        self.current_reward, multiplier = calculate_reward(budget_before_spin, self.bet_counter, self.current_bet) 
        self.final_result = spin_reels(self.current_reward, multiplier) #restituisce una tupla di 3 simboli, ad esempio ("cherry", "cherry", "lemon")
        
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
            # Re-enable only if session is not over (bet 60 disables permanently in show_final_result)
            if self.bet_counter < TOTAL_SESSION_BETS:
                self.spin_btn.setDisabled(False)

    def show_final_result(self):
        r1, r2, r3 = self.final_result #estraggo i simboli del risultato finale

        self.reel1.setPixmap(self.symbols[r1].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        self.reel2.setPixmap(self.symbols[r2].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))
        self.reel3.setPixmap(self.symbols[r3].scaledToWidth(self.symbol_size, Qt.SmoothTransformation))

        # reward already computed in on_spin via calculate_reward()
        reward = self.current_reward
        
        # Fino a questo punto è stato già fatto: coins = coins - bet 
        # gain_visualizzato (reward) = bet * multiplier
        # gain_reale = bet * multiplier - bet
        # quindi facendo coins + reward (gain visualizzato) 
        # -> coins effettivi post giocata = coins + bet*multiplier - bet
        # -> coins + gain_reale = (coins - bet) + gain_visualizzato
        self.coins += reward
        self.update_coin_label()
        self.validate_bet()

        # Compute result_gain: +reward for wins, -bet for losses
        result_gain = reward if reward > 0 else -self.current_bet

        # LOG BET (consolidated event): bet number, bet, result, coin
        try:
            bet_number = self.bet_counter
        except AttributeError:
            bet_number = 0

        self._metrics.log_bet(
            bet_number=bet_number,
            bet=self.current_bet,
            result_gain=result_gain,
            current_coin=self.coins,
        )

        if reward > 0:
            play_sfx("win.wav")
            self.watermark.setText(f"Hai vinto +{reward:.2f}")
        else:
            self.watermark.setText("Try again!")

        # FIX: auto-close AFTER bet 60 is fully processed and logged.
        # Old location (on_spin before processing) required a 61st press.
        if self.bet_counter >= TOTAL_SESSION_BETS:
            self.spin_btn.setDisabled(True)
            QTimer.singleShot(1500, self.close)


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
        sys.exit()
        
    
    
    # ------------------------------------------------------------------
    #     ISTANCE METHODS TO ACCESS WINDOW INFO (for slot_logic): 
    #     self.coins; self.current_bet, self.bet_counter
    # ------------------------------------------------------------------
    def get_current_bet_counter(self) -> int:
        return self.bet_counter
    
    def get_current_bet(self) -> float:
        return self.current_bet
    
    def get_current_coins(self) -> float:
        return self.coins
    
    # ------------------------------------------------------------------
    # TESTING STATISTICS (TEST MODE)
    # ------------------------------------------------------------------
    
    # Creato per includere on_spin() logic + show_final_result() logic in un unico metodo sincrono, da usare in testing_statistics() per evitare i 4 secondi di attesa dell'animazione QTimer. Non è chiamato da nessuna altra parte.   
    def _execute_spin_logic(self) -> None:
        """Spin sincrono senza animazione QTimer. Usato solo da testing_statistics().

        Equivale a on_spin() + show_final_result() ma termina immediatamente,
        consentendo l'uso in un loop senza attendere i ~4 secondi di animazione.
        Mirrors the EXACT same pipeline as the real gameplay path:
          budget_before_spin → deduct bet → calculate_reward → spin_reels → add reward → log
        """
        if self.current_bet <= 0 or self.current_bet > self.coins:
            return  # puntata non valida: salta lo spin

        # increment bet counter (mirrors on_spin)
        self.bet_counter += 1

        # CORRECT: same pipeline as on_spin + show_final_result
        budget_before_spin = self.coins                                                     # snapshot before deduction
        self.coins -= self.current_bet                                                      # deduct bet
        reward, multiplier = calculate_reward(budget_before_spin, self.bet_counter, self.current_bet)  # deterministic reward
        r1, r2, r3 = spin_reels(reward, multiplier)                                        # symbol selection from reward
        self.coins += reward                                                                # apply reward

        # compute result_gain (+reward or -bet)
        result_gain = reward if reward > 0 else -self.current_bet

        # consolidated log entry for the bet
        self._metrics.log_bet(
            bet_number=self.bet_counter,
            bet=self.current_bet,
            result_gain=result_gain,
            current_coin=self.coins,
        )

        # Auto-close after the configured number of bets
        if self.bet_counter >= TOTAL_SESSION_BETS:
            print(f"[TEST] Sessione completata: {self.bet_counter} puntate loggate.")
            self.close() 
                       

    def testing_statistics(self) -> None:
        """Simula una sessione completa di TOTAL_SESSION_BETS puntate consecutive in TEST MODE.

        Chiamata da main.py quando researcher.test_mode è True, subito dopo window.show()
        e prima che app.exec_() venga avviato.

        Comportamento:
        - Resetta lo stato della sessione (coins=INITIAL_BUDGET, bet_counter=0).
        - enable_metrics è già chiamato da RemoteResearcher.start_metrics() prima di questa.
        - Esegue esattamente TOTAL_SESSION_BETS spin sincroni via _execute_spin_logic(),
          ciascuno con una puntata casuale tra MIN_BET e MAX_BET (step BET_STEP).
        - All'ultima puntata (bet_counter == TOTAL_SESSION_BETS) _execute_spin_logic chiama
          self.close() → closeEvent → SESSION_END loggato automaticamente.

        Resistente alle future modifiche di slot_logic.py: tutta la logica di vincita/perdita
        è delegata a _execute_spin_logic → spin_reels() → calculate_reward(), esattamente
        come avverrebbe in una sessione reale dell'utente.

        Al riavvio dell'app una nuova sessione viene appesa al CSV esistente.
        """
        # Inizializza stato sessione come in una vera partita
        self.coins = INITIAL_BUDGET
        self.bet_counter = 0
        self.current_bet = MIN_BET  # valore iniziale; verrà sovrascritto ad ogni iterazione del loop

        # Reset phase-global budget variables in slot_logic before each TEST session.
        # Without this, a second TEST run would use stale initial_budget_X from the previous session.
        import core.slot_logic as _sl
        _sl.initial_budget_before = None
        _sl.initial_budget_during = None
        _sl.initial_budget_after  = None

        # enable_metrics already called by RemoteResearcher.start_metrics() — no need to repeat here.
        self.update_coin_label()
        self.update_bet_display()

        # Simula esattamente 60 puntate consecutive, ciascuna con puntata casuale [MIN_BET, MAX_BET].
        # Al termine dell'ultima, _execute_spin_logic chiama self.close() → SESSION_END.
        for _ in range(TOTAL_SESSION_BETS):
            # Random bet from MIN_BET to MAX_BET (inclusive) in BET_STEP increments: poichè random crea seq interi, prima la creo sulle decine, poi divido per 10
            self.current_bet = random.choice(range(int(MIN_BET*10), int(MAX_BET*10)+1, int(BET_STEP*10))) / 10.0
            self._execute_spin_logic()
