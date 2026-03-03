import random

# REPEAT CONSTANTS TO AVOID CIRCULAR IMPORTS
INITIAL_BUDGET = 100.0
TOTAL_SESSION_BETS = 60
PHASE_LENGTH = 20


# CONSTANTS
PHASES = {
    "PHASE_BEFORE": range(1, PHASE_LENGTH + 1),
    "PHASE_DURING": range(PHASE_LENGTH + 1, 2 * PHASE_LENGTH + 1),
    "PHASE_AFTER": range(2 * PHASE_LENGTH + 1, TOTAL_SESSION_BETS + 1),
}

# List of symbols
SYMBOLS = ["banana", "bar", "bell", "cherry", "diamond", "grape", "lemon", "seven", "star"]

# Game conditions
#VALID_CONDITIONS = ["EQUAL", "WIN", "LOSE"]  # EQUAL, WIN, LOSE
VALID_CONDITIONS = {
    "E": "EQUAL",
    "W": "WIN",
    "L": "LOSE"}

# Global variable
# win_percentage = 0.2 

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

# Variabili globali
initial_budget_before, initial_budget_during, initial_budget_after = None, None, None
condition = "EQUAL"  # default condition, can be updated by researcher input

def update_condition(input_condition: str) -> None:
    global condition
    condition = input_condition
        

def calculate_reward(budget_before_spin, current_bet_counter, current_bet):
    ''' 
        Ogni volta che entriamo nella fase
        - verifico se la bet corrisponde ad una vincita/perdita di quella fase
            - se vittoria: 
              calcolo l'initial budget della fase e lo salvo in una variabile globale: initial_budget_before, initial_budget_during, initial_budget_after
              valuto la vittoria: calcola sia la reward che il moltiplicatore usato per calcolarla
            - altrimenti: pass

        - 
    '''
    global initial_budget_before, initial_budget_during, initial_budget_after, condition
    # FASI: da 1-20 -> PHASE_BEFORE, da 21-40 -> PHASE_DURING, da 41-60 -> PHASE_AFTER
    
    # ----------FASE BEFORE----------
    if current_bet_counter in PHASES["PHASE_BEFORE"]:
        if initial_budget_before is None:
            initial_budget_before = INITIAL_BUDGET
        print(f"FASE BEFORE {current_bet_counter}, initial budget: {initial_budget_before:.2f}, budget: {budget_before_spin:.2f}, bet: {current_bet}")

        win = BEFORE_AFTER_PHASE[current_bet_counter]
        if win:
            # calcolo reward attesa di questa fase: vince tutto ciò che ha perso fino ad ora
            reward, multiplier = loss_recover(initial_budget_before, budget_before_spin, current_bet_counter, current_bet)
            return (reward, multiplier)
        return (0, None)


    # ----------FASE DURING----------
    if current_bet_counter in PHASES["PHASE_DURING"]:
        if initial_budget_during is None:
            initial_budget_during = budget_before_spin # il budget iniziale della fase during è quello ottenuto alla fine della fase before
        print(f"FASE DURING {current_bet_counter}: initial budget: {initial_budget_during:.2f}, condizione {condition}, bet corrente: {current_bet}, guadagno W, perdita L, stabili E")
        # EQUAL
        if condition == "EQUAL":
            win = DURING_PHASE_EQUAL[current_bet_counter]
            if win:
                reward, multiplier = loss_recover(initial_budget_during, budget_before_spin, current_bet_counter, current_bet)
                return reward, multiplier
            return 0, None
        # WIN
        elif condition == "WIN":
            win = DURING_PHASE_WIN[current_bet_counter]
            if win:
                reward, multiplier = win_increase(current_bet_counter, current_bet)
                return reward, multiplier
            return 0, None
        # LOSE
        elif condition == "LOSE":
            win = DURING_PHASE_LOSE[current_bet_counter]
            if win:
                reward, multiplier = lose_increase(budget_before_spin, current_bet_counter, current_bet)
                return reward, multiplier
            return 0, None
        else:
            raise ValueError(f"Invalid condition: {condition}")
    
    
    # ----------FASE AFTER----------
    if current_bet_counter in PHASES["PHASE_AFTER"]:
        # uguale alla fase before: arrivo alla 41 inclusa
        if initial_budget_after is None:
            initial_budget_after = budget_before_spin # il budget iniziale della fase after è quello ottenuto alla fine della fase during
        print(f"FASE AFTER {current_bet_counter}: initial budget: {initial_budget_after:.2f}, bet corrente: {current_bet}, rimanere nell'intorno di initial_budget_after")
        
        win = BEFORE_AFTER_PHASE[current_bet_counter - 40]  # usa la stessa mappa della fase before, ma con indice corretto (1-20)
        if win:
            reward, multiplier = loss_recover(initial_budget_after, budget_before_spin, current_bet_counter, current_bet)
            return (reward, multiplier)
        return (0, None)


def loss_recover(initial_budget_phase, budget_before_spin, current_bet_counter, current_bet):
    """
    Logica condivisa per BEFORE, AFTER e DURING-EQUAL:
    la reward recupera esattamente la perdita cumulata dalla fase + la bet corrente.
    """
    # diversamente dall'excell: bisogna ritornare la reward effettiva (e visualizzata)
    # ovvero il valore totale inclusa la bet (che ho già tolto dai coins non appena si clicca spin)    
    expected_reward = round(initial_budget_phase - budget_before_spin + current_bet, 2)
    multiplier = calculate_multiplier(expected_reward, current_bet)
    reward = round(current_bet * multiplier, 2)
    print(f"VITTORIA! Bet n° {current_bet_counter} (moltiplicatore: {multiplier}x) -> current_bet: {current_bet}, expected_reward: {expected_reward}, reward: {reward}")
    return reward, multiplier

# PER DURING_WIN
def win_increase(current_bet_counter, current_bet):
    # estraggo l'incremento percentuale atteso per questa bet, in base alla mappa EXPECTED_PERCENTAGE_INCREASES
    # default 0 if bet not in map: expected_reward = current_bet (minimal win)
    expected_percentage_increase = EXPECTED_PERCENTAGE_INCREASES.get(current_bet_counter, 0)
    expected_reward = round(expected_percentage_increase * initial_budget_during + current_bet, 2)
    multiplier = calculate_multiplier(expected_reward, current_bet)
    reward = round(current_bet * multiplier, 2)
    print(f"VITTORIA! Bet n° {current_bet_counter} (moltiplicatore: {multiplier}x) -> current_bet: {current_bet}, expected_reward: {expected_reward}, reward: {reward}")
    return reward, multiplier

# PER DURING_LOSE
def lose_increase(budget_before_spin, current_bet_counter, current_bet):
    # dai calcoli evito l'uso della puntata, tanto ho una differenza che la eliminerebbe
    lose_value = round(initial_budget_during - budget_before_spin, 2) # calcolo la perdita effettiva cumulata fino ad ora, includendo la bet corrente
    # in questo caso avrò sempre un valore perchè i checkpoints sono fissi
    if current_bet_counter in EXPECTED_PERCENTAGE_DECREASES:
        expected_percentage_decrease = EXPECTED_PERCENTAGE_DECREASES[current_bet_counter]
    else:
        raise ValueError(f"Expected percentage decrease not defined for bet number {current_bet_counter}. Check EXPECTED_PERCENTAGE_DECREASES map.")

    expected_lose_value = round(expected_percentage_decrease * initial_budget_during, 2) # calcolo la perdita attesa per questa bet
    lose_difference = lose_value - expected_lose_value # calcolo la differenza tra perdita effettiva e perdita attesa
    
    # se la perdita effettiva è maggiore di quella attesa, allora do contentino
    if lose_difference > 0: # lose_value > expected_lose_value
        multiplier = calculate_multiplier(lose_difference, current_bet)
        reward = round(current_bet * multiplier, 2)
        print(f"CHECKPOINT WIN CONTENTINO! Bet n° {current_bet_counter} (moltiplicatore: {multiplier}x) -> lose_difference: {lose_difference}, current_bet: {current_bet}, expected_lose_value: {expected_lose_value}, lose_value: {lose_value}, reward: {reward}")
        return reward, multiplier
    # altrimenti non hai perso abbastanza
    else: # lose_value < expected_lose_value
        multiplier = 1 # il minimo per dare una ricompensa più piccola possibile al checkpoint
        reward = round(current_bet * multiplier, 2)
        print(f"CHECKPOINT WIN MINIMO! Bet n° {current_bet_counter} (moltiplicatore: {multiplier}x) -> lose_difference: {lose_difference}, current_bet: {current_bet}, expected_lose_value: {expected_lose_value}, lose_value: {lose_value}, reward: {reward}")
        return reward, multiplier


def calculate_multiplier(expected_reward, current_bet):
    ideal_multiplier = round(expected_reward / current_bet, 0) 
    # NOTE per WIN e LOSE: se non trovo gli expected_percentage-> WIN: expected_reward = current_bet -> multplier = 1 ; LOSE: non avviene mai
    if ideal_multiplier in REWARD_TABLE_MUL:
        multiplier = ideal_multiplier
    else : # REAL_MULTIPLIER
        real_multiplier = max([m for m in REWARD_TABLE_MUL.keys() if m <= ideal_multiplier], default=min(REWARD_TABLE_MUL.keys())) # default è il min perchè unico caso è quando ho tra 0 e 1
        multiplier = real_multiplier
    return multiplier



def spin_reels(reward, multiplier):
    ''' 
    input: reward attesa, moltiplicatore ideale
    output: simboli da visualizzare (in base alla reward attesa e al moltiplicatore ideale/reale che dipendono dalla tabella REWARD_TABLE_MUL)
    '''    
    # LOSS: prendi simboli diversi a caso dalla lista SYMBOLS
    if reward == 0:
        symbols = random.sample(SYMBOLS, 3) # prendo 3 simboli diversi dalla lista SYMBOLS
        return tuple(symbols)
    
    # WIN: vittoria a 3 o a 2
    if reward > 0:
        if multiplier == None: 
            raise ValueError("Multiplier cannot be None for a win.") 
        symbol, occurrence = REWARD_TABLE_MUL[multiplier]
        # vittoria a 3
        if occurrence == 3:
            return (symbol, symbol, symbol)
        # vittoria a 2
        else: 
            # gestione 2 simboli si vincita uguali
            positions = random.sample([0, 1, 2], 2)  # prendi 2 valori casuali dalla lista, saranno le posizioni (indici)
            result = [None, None, None]
            result[positions[0]] = symbol
            result[positions[1]] = symbol
            # gestione simbolo diverso
            other_pos = [i for i in [0,1,2] if i not in positions][0]
            available_symbols = [s for s in SYMBOLS if s != symbol]
            result[other_pos] = random.choice(available_symbols)
            return tuple(result)
            


# OLD
'''def spin_reels():
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
'''

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
