import random

# Constants
# List of symbols
SYMBOLS = ["banana", "bar", "bell", "cherry", "diamond", "grape", "lemon", "seven", "star"]

# Reward table
REWARD_TABLE = {
    "seven": {"3": 100, "2": 10},
    "bar": {"3": 50, "2": 5},
    "bell": {"3": 40, "2": 4},
    "star": {"3": 30, "2": 3},
    "diamond": {"3": 25, "2": 2},
    "cherry": {"3": 20, "2": 2},
    "banana": {"3": 15, "2": 1},
    "grape": {"3": 15, "2": 1},
    "lemon": {"3": 10, "2": 1},
}

CONVERTING_TABLE = {
    10: 0.813,
    3: 0.244,
    1.5: 0.1216,
    1: 0.081,
    0.67: 0.0545,
    0.33: 0.027,
    0.1: 0.008
}
# valori attesi 
'''
valore atteso(IN)	    win_percentage(OUT)
10	                    0.813
3	                    0.244
1.5	                    0.1216
1	                    0.081
0.67	                0.0545
0.33	                0.027
0.1	                    0.008
'''
def update_expected_value(expected_value):
    #VALORE ATTESO: modificato con input del ricercatore
    global win_percentage
    win_percentage = CONVERTING_TABLE[expected_value] #PARAMETRO VINCITA che controlla il valore atteso predefinito
        

# FORZAMENTO PROBABILITA' DI VITTORIA PRE DEFINITA: WIN_PERCENTAGE = 20% -> 20% di vittoria (3 o 2 simboli uguali), 80% di perdita (3 simboli diversi)
#TODO: MODIFICARE TUTTO QUANTO CON LOGICA PREDEFINITA DI VITTORIA, NO VALORI ATTESI
def spin_reels():
    '''Simulates a slot machine spin and returns three symbols as a tuple.

    This function implements a weighted random selection algorithm that controls
    the overall win probability through the WIN_PERCENTAGE global variable.

    Behavior:
        - WIN_PERCENTAGE chance: Returns a winning combination
            - 30% of wins: 3 matching symbols (e.g., ('🍒', '🍒', '🍒'))
            - 70% of wins: 2 matching symbols (e.g., ('🍒', '🍋', '🍒'))
        - (100 - WIN_PERCENTAGE)% chance: Returns 3 different symbols (loss)

    Returns:
        tuple: A tuple of 3 symbols representing the slot machine reels.
               Symbols are selected from the global SYMBOLS list.

    Examples:
        >>> spin_reels()  # Winning spin (3-of-a-kind)
        ('🍒', '🍒', '🍒')
        
        >>> spin_reels()  # Winning spin (2-of-a-kind)
        ('🍋', '🍒', '🍒')
        
        >>> spin_reels()  # Losing spin
        ('🍒', '🍋', '🍊')

    Notes:
        - Requires global variables: WIN_PERCENTAGE (float, 0-100) and SYMBOLS (list)
        - Uses random module for probability calculations
        - For 2-of-a-kind wins, matching symbols are placed in random positions
    '''
    """
    Spins the slot machine and returns 3 symbols (tuple).
    WIN_PERCENTAGE controls overall win probability (3 or 2 matching symbols).
    """
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


def calculate_reward(result, bet_multiplier=1.0):
    """
    Calculates the reward based on the result list: [symbol1, symbol2, symbol3]
    Applies bet_multiplier to the base reward from REWARD_TABLE.
    """
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
