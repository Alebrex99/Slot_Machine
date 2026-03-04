import random
from core.constants import INITIAL_BUDGET, TOTAL_SESSION_BETS, PHASE_LENGTH
from core.constants import PHASES, SYMBOLS, EXPECTED_PERCENTAGE_INCREASES, EXPECTED_PERCENTAGE_DECREASES, REWARD_TABLE_MUL, BEFORE_AFTER_PHASE, DURING_PHASE_EQUAL, DURING_PHASE_WIN, DURING_PHASE_LOSE

# REPEAT CONSTANTS TO AVOID CIRCULAR IMPORTS (updated: import from constants.py)

# VARIABILI GLOBALI
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
    global initial_budget_before, initial_budget_during, initial_budget_after
    # FASI: da 1-20 -> PHASE_BEFORE, da 21-40 -> PHASE_DURING, da 41-60 -> PHASE_AFTER
    
    # ----------FASE BEFORE----------
    if current_bet_counter in PHASES["PHASE_BEFORE"]:
        if initial_budget_before is None:
            initial_budget_before = INITIAL_BUDGET
        print(f"FASE BEFORE {current_bet_counter}: initial budget: {initial_budget_before:.2f}, budget: {budget_before_spin:.2f}, bet: {current_bet}")

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
        print(f"FASE DURING E/W/L {current_bet_counter}: initial budget: {initial_budget_during:.2f}, condizione {condition}, budget: {budget_before_spin:.2f}, bet: {current_bet}")
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
        print(f"FASE AFTER {current_bet_counter}: initial budget: {initial_budget_after:.2f}, budget: {budget_before_spin:.2f}, bet: {current_bet}")
        
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
    if initial_budget_phase - budget_before_spin < 0:
        difference = 0
    else:
        difference = initial_budget_phase - budget_before_spin
    expected_reward = round(difference + current_bet, 2)
    multiplier = calculate_multiplier(expected_reward, current_bet)
    reward = round(current_bet * multiplier, 2)
    print(f"VITTORIA! Bet n° {current_bet_counter}, expected_reward: {expected_reward}, moltiplicatore: {multiplier}x, gain reale: {reward - current_bet}, reward: {reward}")
    return reward, multiplier

# PER DURING_WIN
def win_increase(current_bet_counter, current_bet):
    # estraggo l'incremento percentuale atteso per questa bet, in base alla mappa EXPECTED_PERCENTAGE_INCREASES
    # default 0 if bet not in map: expected_reward = current_bet (minimal win)
    expected_percentage_increase = EXPECTED_PERCENTAGE_INCREASES.get(current_bet_counter, 0)
    expected_reward = round(expected_percentage_increase * initial_budget_during + current_bet, 2)
    multiplier = calculate_multiplier(expected_reward, current_bet)
    reward = round(current_bet * multiplier, 2)
    print(f"VITTORIA! Bet n° {current_bet_counter}, expected_reward: {expected_reward}, expected_%_WIN: {expected_percentage_increase}, moltiplicatore: {multiplier}x, gain reale: {reward - current_bet}, reward: {reward}")
    return reward, multiplier

# PER DURING_LOSE
def lose_increase(budget_before_spin, current_bet_counter, current_bet):
    # Evito di sommare la puntata nei calcoli, tanto ho una differenza che la eliminerebbe
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
        print(f"CHECKPOINT CONTENTINO! Bet n° {current_bet_counter}, lose_value: {lose_value}, expected_lose_value: {expected_lose_value}, lose_difference: {lose_difference}, multiplier: {multiplier}x, gain reale: {reward - current_bet}, reward: {reward}")
        return reward, multiplier
    # altrimenti non hai perso abbastanza
    else: # lose_value < expected_lose_value
        multiplier = 1 # il minimo per dare una ricompensa più piccola possibile al checkpoint
        reward = round(current_bet * multiplier, 2)
        print(f"CHECKPOINT MINIMO! Bet n° {current_bet_counter}, lose_value: {lose_value}, expected_lose_value: {expected_lose_value}, lose_difference: {lose_difference}, multiplier: {multiplier}x, gain reale: {reward - current_bet}, reward: {reward}")
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
