import random

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
    """
    Spins the slot machine and returns 3 symbols (tuple).
    Probability of matching symbols is 20%.
    """
    if random.random() < 0.2: #estrai un nuomero casuale tra 0 e 1, se è minore di 0.2 (20% di probabilità)
        # 20% chance: all 3 symbols are the same
        symbol = random.choice(SYMBOLS)
        return (symbol, symbol, symbol)
    else:
        # 80% chance: random symbols
        return tuple(random.choices(SYMBOLS, k=3))
    #return tuple(random.choices(SYMBOLS, k=3))


def calculate_reward(result):
    """
    Calculates the reward based on the result list: [symbol1, symbol2, symbol3]
    """
    if not result or len(result) != 3:
        return 0

    s1, s2, s3 = result

    # 3 of a kind
    if s1 == s2 == s3:
        return REWARD_TABLE.get(s1, {}).get("3", 0)

    # 2 of a kind
    if s1 == s2 or s2 == s3 or s1 == s3:
        # pick which symbol matched
        match_symbol = s1 if s1 == s2 or s1 == s3 else s2
        return REWARD_TABLE.get(match_symbol, {}).get("2", 0)

    # No match
    return 0
