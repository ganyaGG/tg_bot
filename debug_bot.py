import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_ticker(ticker):
    print(f"\n{'='*50}")
    print(f"Тестирование тикера: {ticker}")
    print(f"{'='*50}")
    
    try:
        # 1. Проверяем через Ticker
        stock = yf.Ticker(ticker)
        info = stock.info
        
        print(f"1. Информация о компании:")
        print(f"   - Название: {info.get('shortName', 'N/A')}")
        print(f"   - Символ: {info.get('symbol', 'N/A')}")
        print(f"   - Рынок: {info.get('exchange', 'N/A')}")
        print(f"   - Валюта: {info.get('currency', 'N/A')}")
        
        # 2. Загружаем исторические данные
        hist = stock.history(period="2y")
        
        print(f"\n2. Исторические данные:")
        print(f"   - Записей: {len(hist)}")
        print(f"   - Колонки: {hist.columns.tolist()}")
        print(f"   - Диапазон дат: {hist.index[0]} - {hist.index[-1]}")
        
        if not hist.empty:
            print(f"   - Последняя цена: ${hist['Close'].iloc[-1]:.2f}")
        
        # 3. Пробуем через download
        print(f"\n3. Тестирование yf.download():")
        data = yf.download(ticker, period="1mo", progress=False)
        print(f"   - Загружено: {len(data)} записей")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    # Тестируем популярные тикеры
    tickers = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "META"]
    
    for ticker in tickers:
        success = test_ticker(ticker)
        if not success:
            print(f"⚠️ Тикер {ticker} не работает")