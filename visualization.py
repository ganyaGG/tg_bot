import matplotlib.pyplot as plt
import io
import numpy as np

class Visualizer:
    def create_forecast_plot(self, historical, forecast, ticker):
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Исторические данные
        ax.plot(historical, label='История', linewidth=2, color='blue', alpha=0.8)
        
        # Прогноз
        forecast_x = range(len(historical), len(historical) + len(forecast))
        ax.plot(forecast_x, forecast, label='Прогноз на 30 дней', 
                linewidth=3, linestyle='--', color='red')
        
        # Заполняем область прогноза
        ax.fill_between(forecast_x, 
                       forecast * 0.95, 
                       forecast * 1.05, 
                       alpha=0.2, color='red')
        
        ax.set_xlabel('Дни', fontsize=12)
        ax.set_ylabel('Цена ($)', fontsize=12)
        ax.set_title(f'Прогноз цен акций {ticker}', fontsize=16, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Сохраняем в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        return buf