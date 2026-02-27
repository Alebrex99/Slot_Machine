import random
#importiamo l'oggetto creato nel main.py window per accedere alle funzioni getters
from main import window
from gui.main_window import INITIAL_BUDGET, BET_STEP, TOTAL_SESSION_BETS, PHASE_LENGTH

# CONSTANTS
# List of symbols
SYMBOLS = ["banana", "bar", "bell", "cherry", "diamond", "grape", "lemon", "seven", "star"]

# Game conditions
#VALID_CONDITIONS = ["EQUAL", "WIN", "LOSE"]  # EQUAL, WIN, LOSE
VALID_CONDITIONS = {
    "E": "EQUAL",
    "W": "WIN",
    "L": "LOSE"}

# Global variable
win_percentage = 0.2  #TODO mantenuta solamente per far funzionare, dovrò cambiare tutto!

# Fixed parameters
INCREMENTI_PERCENTUALE_ATTESI = []
DECREMENTI_PERCENTUALE_ATTESI = []
RESULT_DECISIONS = [] #lista di esiti prestabiliti: ogni puntata si sa già se vinto/perso

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
# mi serve una tabella per effettuare una ricerca partendo dal moltiplicatore calcolato e ottenre il simbolo da visualizzare e il numero di ccorrenze
REWARD_TABLE = {
    1: {"symbol": "lemon", "occurrences": 2},
    2: {"symbol": "grape", "occurrences": 2},
    3: {"symbol": "banana", "occurrences": 2},
    4: {"symbol": "cherry", "occurrences": 2},
    5: {"symbol": "diamond", "occurrences": 2},
    7: {"symbol": "star", "occurrences": 2},
    8.5: {"symbol": "bell", "occurrences": 2},
    10: {"symbol": "bar", "occurrences": 2},
    12: {"symbol": "seven", "occurrences": 2},
    
    15: {"symbol": "lemon", "occurrences": 3},
    20: {"symbol": "grape", "occurrences": 3},
    30: {"symbol": "banana", "occurrences": 3},
    40: {"symbol": "cherry", "occurrences": 3},
    50: {"symbol": "diamond", "occurrences": 3},
    75: {"symbol": "star", "occurrences": 3},
    100: {"symbol": "bell", "occurrences": 3},
    125: {"symbol": "bar", "occurrences": 3},
    150: {"symbol": "seven", "occurrences": 3},
}

# TODO: completare le mappe -> indica, in corrispondenza della specifica puntata (ottieni il counter e cerchi nella mappa), 
# se quella puntata è una vittoria (1) o una sconfitta (0). 60 puntate per giocatore. 3 mappe diverse solo per la fase DURANTE
BEFORE_AFER_PHASE = { 
    0: 0,
    1: 0,
    2: 1,
}

DURING_PHASE_EQUAL = {
    0: 0,
    1: 1,
    2: 0,
}
DURING_PHASE_WIN = {
    0: 0,
    1: 1,
    2: 1,
}
DURING_PHASE_LOSE = {
    0: 0,
    1: 0,
    2: 1,
}

def update_condition(input_condition: str) -> None:
    #TODO: implementare logica di aggiornamento dei parametri in base alla condition, attualmente non fa nulla
    global condition
    condition = input_condition
    if condition == "EQUAL":
        pass
    elif condition == "WIN":
        pass
    elif condition == "LOSE":
        pass
        

#TODO: MODIFICARE TUTTO QUANTO CON LOGICA PREDEFINITA DI VITTORIA, NO VALORI ATTESI
def spin_reels():
    # genero un numero casuale (distr. uniforme) tra 0 e 1. Quindi la variabile X<a% è vera con probabilità a%
    # win_percentage è già un valore decimale (es. 0.244 = 24.4%), NON va diviso per 100
    if random.random() < win_percentage:
        # WIN = Probabilità di vittoria con 3 simboli uguali o 2 simboli uguali
        # P (3-of-a-kind) = 30% delle vittorie, P (2-of-a-kind) = 70% delle vittorie
        # P (3-of-a-kind) = 0.3 * WIN_PERCENTAGE = 0.3*0.2 = 6%, P (2-of-a-kind) = 0.7 * WIN_PERCENTAGE = 0.7*0.2 = 14% -> totale 20% di vittoria
        if random.random() < 0.3:  # 30% of wins are 3-of-a-kind
            symbol = random.choice(SYMBOLS) #1/9 di scegliere un simbolo
            return (symbol, symbol, symbol)
        else:  # 70% of wins are 2-of-a-kind
            symbol = random.choice(SYMBOLS) # Simbolo che si ripete 2 volte
            positions = random.sample([0, 1, 2], 2)  # prendi 2 valori casuali dalla lista, saranno le posizioni (indici)
            result = [None, None, None]
            # Metti i simboli uguali nelle posizioni scelte
            result[positions[0]] = symbol
            result[positions[1]] = symbol
            # Calcolo la posizione del simbolo diverso, che è l'indice che non è in positions
            # Other_pos -> positions sarebbe [0, 1] o [0, 2] o [1, 2], quindi prendo l'indice che non è in positions
            # es. se positions è [0, 1], allora other_pos sarà 2; se positions è [0, 2], allora other_pos sarà 1; se positions è [1, 2], allora other_pos sarà 0
            other_pos = [i for i in [0, 1, 2] if i not in positions][0] #crea una lista e prendi il primo valore
            # available è la lista dei simboli disponibili per il terzo simbolo, che deve essere diverso da quello scelto per i due simboli uguali
            available = [s for s in SYMBOLS if s != symbol]
            result[other_pos] = random.choice(available)
            return tuple(result)
    else:
        # LOSS = (100 - WIN_PERCENTAGE)% chance: all symbols different
        symbols = random.sample(SYMBOLS, 3) # prendo 3 simboli diversi dalla lista SYMBOLS
        return tuple(symbols)
        #result = []
        #available = SYMBOLS.copy()
        #for _ in range(3):
        #    symbol = random.choice(available)
        #    result.append(symbol)
        #    available.remove(symbol)
        #return tuple(result)

#TODO modificare l'intera logica di reward, ora la slot è truccata!


def calculate_reward(initial_budget, budget_win, current_bet):
    ''' VITTORIA (reward) = BUDGET_INIZIALE (initial_budget) - BUDGET_WIN (prima dello spin) + PUNTATA (current_bet)
     BUDGET_CORRENTE (current_bet) = BUDGET_WIN (prima dello spin) - PUNTATA 
     BUDGET_WIN = BUDGET_CORRENTE + PUNTATA'''
    return initial_budget - budget_win + current_bet


# OLD
"""def calculate_reward(result, bet_multiplier=1.0):
    if not result or len(result) != 3:
        return 0

    s1, s2, s3 = result

    # 3 of a kind
    if s1 == s2 == s3:
        base_reward = REWARD_TABLE.get(s1, {}).get("3", 0)
        return round(base_reward * bet_multiplier, 2)

    # 2 of a kind
    if s1 == s2 or s2 == s3 or s1 == s3:
        # pick which symbol matched
        match_symbol = s1 if s1 == s2 or s1 == s3 else s2
        base_reward = REWARD_TABLE.get(match_symbol, {}).get("2", 0)
        return round(base_reward * bet_multiplier, 2)

    # No match
    return 0
"""