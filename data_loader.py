import yfinance as yf
import numpy as np
from datetime import datetime

class DataLoader:
    def download_data(self, ticker):
        try:
            print(f"Загрузка данных для {ticker}...")
            
            # Используем yfinance для загрузки данных
            stock = yf.Ticker(ticker)
            
            # Пробуем разные периоды
            periods = ["1y", "6mo", "3mo", "1mo"]
            
            for period in periods:
                try:
                    hist = stock.history(period=period)
                    
                    if not hist.empty and len(hist) > 20:
                        print(f"✅ Успешно загружено {len(hist)} записей (период: {period})")
                        
                        # Получаем цены закрытия
                        if 'Close' in hist.columns:
                            prices = hist['Close'].values
                        else:
                            # Берем первую числовую колонку
                            for col in hist.columns:
                                if hist[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
                                    prices = hist[col].values
                                    break
                            else:
                                prices = hist.iloc[:, 0].values
                        
                        # Проверяем, что есть данные
                        if len(prices) > 0 and not np.isnan(prices[-1]):
                            print(f"Последняя цена: {prices[-1]:.2f}")
                            return prices
                
                except Exception as e:
                    print(f"⚠️ Не удалось загрузить период {period}: {e}")
                    continue
            
            print(f"❌ Не удалось загрузить данные для {ticker}")
            return None
            
        except Exception as e:
            print(f"❌ Критическая ошибка при загрузке {ticker}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def download_data_simple(self, ticker):
        """Упрощенная версия загрузки данных"""
        try:
            print(f"[ПРОСТАЯ ЗАГРУЗКА] {ticker}...")
            
            # Прямая загрузка через download
            data = yf.download(ticker, period="1mo", progress=False)
            
            if data.empty:
                print(f"❌ Нет данных для {ticker}")
                return None
            
            # Берем цену закрытия
            if 'Close' in data.columns:
                prices = data['Close'].values
            else:
                prices = data.iloc[:, 0].values
            
            print(f"✅ Загружено {len(prices)} записей")
            print(f"Последняя цена: {prices[-1] if len(prices) > 0 else 'N/A'}")
            
            return prices
            
        except Exception as e:
            print(f"❌ Ошибка простой загрузки: {e}")
            return None