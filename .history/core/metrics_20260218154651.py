#salvataggio di metriche all'interno dell'applicazione. le funzioni saranno invocate 
#dalla main_window ad ogni evento e l'effetto sarà salvare i dati in un file .csv
import csv

def write_to_csv(data):
    # Scrive i dati in un file CSV
    #columns: TIMESTAMP | EVENT_TYPE | BET | EXPECTED_VALUE | RESULT | COIN | MESSAGE
    '''TIMESTAMP | EVENT_TYPE | BET | EXPECTED_VALUE | RESULT | COIN | MESSAGE'''
    
    
    with open('metrics.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)
