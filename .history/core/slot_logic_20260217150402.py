import random

# Constants
WIN_PERCENTAGE = 20

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
    if random.random() < (WIN_PERCENTAGE / 100):
        # WIN_PERCENTAGE chance: winning spin (3 or 2 matching symbols)
        if random.random() < 0.3:  # 30% of wins are 3-of-a-kind
            symbol = random.choice(SYMBOLS)
            return (symbol, symbol, symbol)
        else:  # 70% of wins are 2-of-a-kind
            symbol = random.choice(SYMBOLS)
            positions = random.sample([0, 1, 2], 2)  # Pick 2 positions to match
            result = [None, None, None]
            # metti i simboli uguali nelle posizioni scelte
            result[positions[0]] = symbol
            result[positions[1]] = symbol
            # Third position gets a different symbol
            # positions sarebbe [0, 1] o [0, 2] o [1, 2], quindi prendo l'indice che non è in positions
            # es. se positions è [0, 1], allora other_pos sarà 2; se positions è [0, 2], allora other_pos sarà 1; se positions è [1, 2], allora other_pos sarà 0
            other_pos = [i for i in [0, 1, 2] if i not in positions][0] #crea una lista e prendi il primo valore
            available = [s for s in SYMBOLS if s != symbol]
            result[other_pos] = random.choice(available)
            return tuple(result)
    else:
        # (100 - WIN_PERCENTAGE)% chance: all symbols different (loss)
        result = []
        available = SYMBOLS.copy()
        for _ in range(3):
            symbol = random.choice(available)
            result.append(symbol)
            available.remove(symbol)
        return tuple(result)


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
