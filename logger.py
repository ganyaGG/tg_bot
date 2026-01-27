import csv
import os
from datetime import datetime

class Logger:
    def __init__(self, log_file="logs/logs.csv"):
        self.log_file = log_file
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Создаем файл с заголовком если его нет
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'user_id', 'ticker', 'amount',
                    'best_model', 'rmse', 'mape', 'profit'
                ])
    
    def log_request(self, user_id, ticker, amount, best_model, metrics, profit):
        try:
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    user_id,
                    ticker,
                    amount,
                    best_model,
                    metrics.get('RMSE', 0) if metrics else 0,
                    metrics.get('MAPE', 0) if metrics else 0,
                    profit
                ])
        except Exception as e:
            print(f"[LOGGER] Ошибка логирования: {e}")