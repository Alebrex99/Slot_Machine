#classe per il salvataggio di metriche all'interno dell'applicazione. le funzioni saranno invocate 
#dalla main_window ad ogni evento e l'effetto sarà salvare i dati in un file .csv
import csv
class Metrics():
    def __init__(self):
        pass
    
    def write_to_csv(self, data):
        # Scrive i dati in un file CSV
        with open('metrics.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

