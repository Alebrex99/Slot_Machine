# Tutte le costanti condivise tra gui e core
# Nessun import da altri moduli interni → nessun rischio di circolarità

# -----------------GAME CONSTANTS-------------------
INITIAL_BUDGET: float = 100.0
MIN_BET: float = 0.10
MAX_BET: float = 2.0
BET_STEP: float = 0.10
TOTAL_SESSION_BETS: int = 60
PHASE_LENGTH: int = 20
TOTAL_TESTS: int = 50
MESSAGE_COUNTER_POINT = 40  # punto in cui mostrare il messaggio a metà sessione (dopo 40 scommesse, all'inizio della fase AFTER)
MESSAGE_TIMER = 30  # secondi per cui mostrare il messaggio a metà sessione

# ---------------REMOTE RESEARCHER CONSTANTS-----------------
VALID_CONDITIONS = {
    "E": "EQUAL",
    "W": "WIN",
    "L": "LOSE"}


# -----------------SLOT LOGIC CONSTANTS-------------------
PHASES = {
    "PHASE_BEFORE": range(1, PHASE_LENGTH + 1),
    "PHASE_DURING": range(PHASE_LENGTH + 1, 2 * PHASE_LENGTH + 1),
    "PHASE_AFTER": range(2 * PHASE_LENGTH + 1, TOTAL_SESSION_BETS + 1),
}

# List of symbols
SYMBOLS = ["banana", "bar", "bell", "cherry", "diamond", "grape", "lemon", "seven", "star"]

# Fixed parameters
# valori percentuali attesi: salvo l'indice di vittoria e il valore
EXPECTED_PERCENTAGE_INCREASES = {
    21: 0.025,
    23: 0.025,
    24: 0.08,
    26: 0.005,
    27: 0.05,
    29: 0.05,
    32: 0.025,
    33: 0.05,
    35: 0.15,
    37: 0.04,
    38: 0.075,
    39: 0.075,
    40: 0.15
}
EXPECTED_PERCENTAGE_DECREASES = {25: 0.05, 30: 0.15, 35: 0.15}

# mi serve una tabella per effettuare una ricerca partendo dal moltiplicatore calcolato e ottenre il simbolo da visualizzare e il numero di ccorrenze
REWARD_TABLE_MUL = {
    1: ("lemon", 2),
    2: ("grape", 2),
    3: ("banana", 2),
    4: ("cherry", 2),
    5: ("diamond", 2),
    7: ("star", 2),
    8.5: ("bell", 2),
    10: ("bar", 2),
    12: ("seven", 2),
    15: ("lemon", 3),
    20: ("grape", 3),
    30: ("banana", 3),
    40: ("cherry", 3),
    50: ("diamond", 3),
    75: ("star", 3),
    100: ("bell", 3),
    125: ("bar", 3),
    150: ("seven", 3),
}

# Deterministic outcome maps: 1 = WIN, 0 = LOSS
# Keys are 0-based bet indices within the phase (0–19 for each 20-bet phase).
#
# BEFORE_AFTER_PHASE: used for PHASE_BEFORE (bets 1–20) and PHASE_AFTER (bets 41–60).
# Goal: player stays roughly flat around their current budget.
# Wins and losses are balanced so net result ≈ 0 over the 20 bets.
BEFORE_AFTER_PHASE = {
    1:  False,  # loss
    2:  False,  # loss
    3:  False,  # loss
    4:  True,   # win
    5:  False,  # loss
    6:  False,  # loss
    7:  True,   # win
    8:  False,  # loss
    9:  False,  # loss
    10: False,  # loss
    11: False,  # loss
    12: True,   # win
    13: False,  # loss
    14: False,  # loss
    15: True,   # win
    16: True,   # win
    17: False,  # loss
    18: False,  # loss
    19: False,  # loss
    20: True,   # win
    # 6 wins, 14 losses
}

# DURING_PHASE_EQUAL: player stays roughly flat around 100 coins during bets 21–40.
# Same win/loss balance as BEFORE_AFTER_PHASE to keep budget stable.
DURING_PHASE_EQUAL = {
    21: False,
    22: False,
    23: False,
    24: True,
    25: False,
    26: False,
    27: True,
    28: False,
    29: False,
    30: False,
    31: False,
    32: True,
    33: False,
    34: False,
    35: True,
    36: True,
    37: False,
    38: False,
    39: False,
    40: True,
    # 6 wins, 14 losses → net ≈ 0 (flat)
}

# DURING_PHASE_WIN: player wins significantly more during bets 21–40.
# More wins than losses → budget trends upward.
DURING_PHASE_WIN = {
    21: True,
    22: False,
    23: True,
    24: True,
    25: False,
    26: True,
    27: True,
    28: False,
    29: True,
    30: False,
    31: False,
    32: True,
    33: True,
    34: True,
    35: True,
    36: True,
    37: True,
    38: True,
    39: True,
    40: True,
    # 16 wins, 4 losses → net positive (upward trend)
}

# DURING_PHASE_LOSE: player loses significantly more during bets 21–40.
# More losses than wins → budget trends downward.
DURING_PHASE_LOSE = {
    21: False,
    22: False,
    23: False,
    24: False,
    25: True,
    26: False,
    27: False,
    28: False,
    29: False,
    30: True,
    31: False,
    32: False,
    33: False,
    34: False,
    35: True,
    36: False,
    37: False,
    38: False,
    39: False,
    40: False,
    # 3 wins, 17 losses → net negative (downward trend)
}




# ----------------UNUSED: OLD-------------------
REWARD_TABLE = {
    "seven": {"3": 150, "2": 12},
    "bar": {"3": 125, "2": 10},
    "bell": {"3": 100, "2": 8.5},
    "star": {"3": 75, "2": 7},
    "diamond": {"3": 50, "2": 5},
    "cherry": {"3": 40, "2": 4},
    "banana": {"3": 30, "2": 3},
    "grape": {"3": 20, "2": 2},
    "lemon": {"3": 15, "2": 1},
}