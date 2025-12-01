import json
import os

REDEEM_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "redeem_codes.json")

# Keep track of used codes in memory (reset on app restart)
used_codes = set()

def validate_redeem_code(code: str) -> int:
    """Return coins if valid, 0 if invalid or already used."""
    code = code.upper().strip()

    if code in used_codes:
        return 0

    if not os.path.exists(REDEEM_FILE):
        print(f"[Warning] Redeem file not found: {REDEEM_FILE}")
        return 0

    with open(REDEEM_FILE, "r") as f:
        try:
            redeem_dict = json.load(f)
        except json.JSONDecodeError:
            print("[Error] Invalid JSON in redeem_codes.json")
            return 0

    if code in redeem_dict:
        coins = redeem_dict[code]
        used_codes.add(code)  # mark as used
        return coins

    return 0
