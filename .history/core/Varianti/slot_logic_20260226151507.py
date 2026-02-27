# Creo la medeima logica della slot_machine in versione classe,
# in questo modo, posso modificare a piacimento la logica di vittoria, usando oggetti diveri, senza dover modificare la logica di gioco o la GUI.
# LOGICA ATTUALE: il sistema delle condizioni senza percnetuale di vittoria, 
# ma slot truccata e vittoria prestabilite
from random import random


class SlotMachine:
    def __init__(self, win_percentage=0.2):
        self.win_percentage = win_percentage
    def spin(self):
        # Simulate a spin and determine if it's a win or loss based on win_percentage
        outcome = random.random() < self.win_percentage
        return outcome