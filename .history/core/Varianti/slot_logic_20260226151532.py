# Creo la medeima logica della slot_machine in versione classe,
# in questo modo, posso modificare a piacimento la logica di vittoria, usando oggetti diveri, senza dover modificare la logica di gioco o la GUI.
# LOGICA ATTUALE: il sistema delle condizioni senza percnetuale di vittoria, 
# ma slot truccata e vittoria prestabilite
from random import random

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


# OLD: Reward table
'''REWARD_TABLE = {
    "seven": {"3": 100, "2": 10},
    "bar": {"3": 50, "2": 5},
    "bell": {"3": 40, "2": 4},
    "star": {"3": 30, "2": 3},
    "diamond": {"3": 25, "2": 2},
    "cherry": {"3": 20, "2": 2},
    "banana": {"3": 15, "2": 1},
    "grape": {"3": 15, "2": 1},
    "lemon": {"3": 10, "2": 1},
}'''
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
# TODO: completare le mappe -> indica, in corrispondenza della specifica puntata (ottieni il counter e cerchi nella mappa), 
# se quella puntata è una vittoria (1) o una sconfitta (0). 60 puntate per giocatore. 3 mappe diverse solo per la fase DURANTE
BEFORE_PHASE = { 
    0: 0,
    1: 0,
    2: 1,
}
AFTER_PHASE = {
    0: 1,
    1: 1,
    2: 0,
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

class SlotMachine:
    def __init__(self, win_percentage=0.2):
        self.win_percentage = win_percentage
    def spin(self):
        # Simulate a spin and determine if it's a win or loss based on win_percentage
        outcome = random.random() < self.win_percentage
        return outcome