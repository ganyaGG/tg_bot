import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

# Упрощенные модели
class SimpleLinearModel:
    def __init__(self):
        self.name = "Линейная модель"
        self.slope = 0
        self.intercept = 0
    
    def train(self, train_data):
        if len(train_data) > 1:
            x = np.arange(len(train_data))
            y = train_data
            self.slope, self.intercept = np.polyfit(x, y, 1)
        return self
    
    def predict(self, last_values, steps=30):
        start_idx = len(last_values)
        predictions = []
        for i in range(steps):
            pred = self.slope * (start_idx + i) + self.intercept
            predictions.append(pred)
        return np.array(predictions)

class MovingAverageModel:
    def __init__(self, window=10):
        self.name = "Скользящее среднее"
        self.window = window
        self.last_avg = 0
    
    def train(self, train_data):
        if len(train_data) >= self.window:
            self.last_avg = np.mean(train_data[-self.window:])
        else:
            self.last_avg = np.mean(train_data) if len(train_data) > 0 else 0
        return self
    
    def predict(self, last_values, steps=30):
        return np.full(steps, self.last_avg)

class ModelSelector:
    def __init__(self):
        self.models = {
            'Линейная модель': SimpleLinearModel(),
            'Скользящее среднее': MovingAverageModel()
        }
        self.best_model = None
        self.best_model_name = None
    
    def train_and_evaluate(self, train_data, test_data):
        metrics = {}
        
        print(f"[MODEL] Обучение моделей, train: {len(train_data)}, test: {len(test_data)}")
        
        for name, model in self.models.items():
            try:
                print(f"[MODEL] Обучение: {name}")
                
                # Обучаем модель
                trained_model = model.train(train_data)
                
                # Прогнозируем
                if len(train_data) >= 10:
                    last_values = list(train_data[-10:])
                else:
                    last_values = list(train_data)
                
                predictions = trained_model.predict(last_values, steps=len(test_data))
                
                if len(predictions) > 0 and len(test_data) > 0:
                    # Рассчитываем метрики
                    rmse = np.sqrt(mean_squared_error(test_data, predictions[:len(test_data)]))
                    mape = mean_absolute_percentage_error(test_data, predictions[:len(test_data)])
                    
                    metrics[name] = {
                        'RMSE': rmse,
                        'MAPE': mape,
                        'model': trained_model
                    }
                    
                    print(f"[MODEL] {name}: RMSE={rmse:.2f}, MAPE={mape:.2%}")
                
            except Exception as e:
                print(f"[MODEL] Ошибка в модели {name}: {e}")
                continue
        
        # Выбираем лучшую модель по RMSE
        if metrics:
            self.best_model_name = min(metrics.items(), key=lambda x: x[1]['RMSE'])[0]
            self.best_model = metrics[self.best_model_name]['model']
            print(f"[MODEL] Лучшая модель: {self.best_model_name}")
        else:
            print("[MODEL] Ни одна модель не сработала, использую линейную по умолчанию")
            self.best_model_name = "Линейная модель"
            self.best_model = SimpleLinearModel()
            self.best_model.train(train_data)
            metrics[self.best_model_name] = {'RMSE': 0, 'MAPE': 0, 'model': self.best_model}
        
        return self.best_model_name, metrics