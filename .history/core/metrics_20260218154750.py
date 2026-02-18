#salvataggio di metriche all'interno dell'applicazione. le funzioni saranno invocate 
#dalla main_window ad ogni evento e l'effetto sarà salvare i dati in un file .csv
import csv

def start_metrics():
    # Crea un file CSV e scrive l'intestazione
    with open('metrics.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['TIMESTAMP', 'EVENT_TYPE', 'BET', 'EXPECTED_VALUE', 'RESULT', 'COIN', 'MESSAGE'])

def log_event(event_type, bet, expected_value, result, coin, message):
    # Logga un evento con i dati forniti
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    data = [timestamp, event_type, bet, expected_value, result, coin, message]
    write_to_csv(data)

def write_to_csv(data):
    # Scrive i dati in un file CSV
    #columns: TIMESTAMP | EVENT_TYPE | BET | EXPECTED_VALUE | RESULT | COIN | MESSAGE
    '''TIMESTAMP | EVENT_TYPE | BET | EXPECTED_VALUE | RESULT | COIN | MESSAGE'''
    
    
    with open('metrics.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)
