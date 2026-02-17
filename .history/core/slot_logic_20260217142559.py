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


def spin_reels() -> tuple[str, str, str]:
    """
    Spins the slot machine and returns 3 symbols (tuple).
    1) WIN_PERCENTAGE of the time returns a winning outcome (either 3-of-a-kind or 2-of-a-kind).
    2) Otherwise returns a non-winning outcome with all three symbols different.
    """
    if len(SYMBOLS) < 3:
        raise ValueError("SYMBOLS must contain at least 3 unique symbols")

    # Decide overall win vs non-win
    if random.random() < (WIN_PERCENTAGE / 100):
        # Winning case: choose between 3-of-a-kind and 2-of-a-kind.
        # Here 3-of-a-kind is rarer within the winning cases (25% vs 75%).
        if random.random() < 0.25:
            symbol = random.choice(SYMBOLS)
            return (symbol, symbol, symbol)
        else:
            pair_symbol = random.choice(SYMBOLS)
            single_symbol = random.choice([s for s in SYMBOLS if s != pair_symbol])
            res = [pair_symbol, pair_symbol, single_symbol]
            random.shuffle(res)
            return tuple(res)
    else:
        # Non-winning: ensure all three symbols are different
        return tuple(random.sample(SYMBOLS, k=3))


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
