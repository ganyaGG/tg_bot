import numpy as np
from scipy.signal import argrelextrema

class TradingStrategy:
    def __init__(self, forecast_prices, initial_investment=1000):
        self.prices = forecast_prices
        self.initial_investment = initial_investment
    
    def find_extremes(self):
        """Находим локальные минимумы и максимумы"""
        if len(self.prices) < 3:
            return [], []
        
        try:
            minima_indices = argrelextrema(self.prices, np.less, order=1)[0]
            maxima_indices = argrelextrema(self.prices, np.greater, order=1)[0]
            return minima_indices.tolist(), maxima_indices.tolist()
        except:
            return [], []
    
    def calculate_profit(self):
        """Расчет потенциальной прибыли"""
        if len(self.prices) < 2:
            return 0
        
        # Простая стратегия: купить в начале, продать в конце
        buy_price = self.prices[0]
        sell_price = self.prices[-1]
        
        shares = self.initial_investment / buy_price
        final_value = shares * sell_price
        profit = final_value - self.initial_investment
        
        return profit
    
    def generate_recommendations(self):
        """Генерация рекомендаций"""
        minima, maxima = self.find_extremes()
        
        recommendations = []
        
        if minima and len(minima) > 0:
            rec = "📈 Дни для покупки: "
            rec += ", ".join([str(i+1) for i in minima[:3]])  # первые 3 минимума
            recommendations.append(rec)
        
        if maxima and len(maxima) > 0:
            rec = "📉 Дни для продажи: "
            rec += ", ".join([str(i+1) for i in maxima[:3]])  # первые 3 максимума
            recommendations.append(rec)
        
        profit = self.calculate_profit()
        profit_percent = (profit / self.initial_investment) * 100 if self.initial_investment > 0 else 0
        
        recommendations.append(f"💰 Потенциальная прибыль: ${profit:.2f} ({profit_percent:+.1f}%)")
        
        if not recommendations:
            recommendations.append("📊 Рекомендуется удерживать позицию")
        
        return "\n".join(recommendations)