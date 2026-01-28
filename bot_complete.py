import asyncio
import sys
import os
import logging
import numpy as np
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("🚀 Бот для анализа акций - ПОЛНАЯ РАБОЧАЯ ВЕРСИЯ")
print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# Импортируем наши модули
from data_loader import DataLoader
from model_selector import ModelSelector
from visualization import Visualizer
from strategy import TradingStrategy
from logger import Logger

# ========== КОНФИГУРАЦИЯ ==========

# ВАЖНО: ЗАМЕНИТЕ ЭТОТ ТОКЕН НА ВАШ!
TELEGRAM_TOKEN = ""


# Инициализация компонентов
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
data_loader = DataLoader()
model_selector = ModelSelector()
visualizer = Visualizer()
strategy_module = TradingStrategy  # Класс, а не экземпляр
app_logger = Logger("logs/logs.csv")

# ========== СОСТОЯНИЯ ==========

class UserState(StatesGroup):
    waiting_ticker = State()
    waiting_amount = State()

# ========== КОМАНДЫ ==========

@dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message):
    """Начало работы с ботом"""
    welcome_text = (
        "📈 *Бот для анализа и прогнозирования акций*\n\n"
        "Я могу:\n"
        "• Загрузить исторические данные акций\n"
        "• Обучить модели прогнозирования\n"
        "• Сделать прогноз на 30 дней\n"
        "• Дать инвестиционные рекомендации\n"
        "• Рассчитать потенциальную прибыль\n\n"
        "📋 *Как использовать:*\n"
        "1. Введите тикер компании (например: AAPL, TSLA, MSFT)\n"
        "2. Введите сумму для условной инвестиции\n"
        "3. Получите анализ и прогноз\n\n"
        "📊 *Примеры тикеров:*\n"
        "• AAPL - Apple\n"
        "• MSFT - Microsoft\n"
        "• TSLA - Tesla\n"
        "• GOOGL - Alphabet (Google)\n"
        "• AMZN - Amazon\n\n"
        "⚠️ *Важно:* Результаты носят учебный характер\n"
        "Не является финансовой рекомендацией.\n\n"
        "Введите тикер компании:"
    )
    
    await message.answer(welcome_text, parse_mode='Markdown')
    await UserState.waiting_ticker.set()

@dp.message_handler(commands=['status'])
async def status_command(message: types.Message):
    """Проверка статуса бота"""
    await message.answer(
        "✅ *Статус бота:* Работает нормально\n"
        f"• Время: {datetime.now().strftime('%H:%M:%S')}\n"
        "• Модели готовы к работе\n"
        "• Источник данных: Yahoo Finance\n\n"
        "Введите /start для начала анализа",
        parse_mode='Markdown'
    )

# ========== ОБРАБОТКА ТИКЕРА ==========

@dp.message_handler(state=UserState.waiting_ticker)
async def process_ticker(message: types.Message, state: FSMContext):
    """Обработка введенного тикера"""
    # Очищаем ввод
    user_input = message.text.strip().upper()
    
    # Берем только первый тикер если введено несколько
    if ',' in user_input:
        ticker = user_input.split(',')[0].strip()
    elif ' ' in user_input:
        ticker = user_input.split()[0].strip()
    else:
        ticker = user_input
    
    print(f"[BOT] Получен тикер: {ticker}")
    
    # Проверка формата
    if len(ticker) > 10 or len(ticker) < 1:
        await message.answer(
            "❌ Неверный формат тикера.\n"
            "Тикер должен содержать 1-5 символов.\n"
            "Примеры: AAPL, MSFT, TSLA"
        )
        return
    
    # Начинаем загрузку
    status_msg = await message.answer(f"⏳ Загружаю данные для *{ticker}*...", parse_mode='Markdown')
    
    # Загрузка данных
    prices = data_loader.download_data(ticker)
    
    if prices is None or len(prices) < 30:
        await status_msg.delete()
        await message.answer(
            f"❌ Не удалось загрузить данные для *{ticker}*.\n"
            f"Проверьте правильность тикера и попробуйте снова.",
            parse_mode='Markdown'
        )
        return
    
    current_price = float(prices[-1])
    
    await status_msg.edit_text(f"✅ Загружено {len(prices)} дней данных")
    
    # Сохраняем данные в состоянии
    await state.update_data({
        'ticker': ticker,
        'prices': prices,
        'current_price': current_price
    })
    
    # Запрашиваем сумму
    await message.answer(
        f"📊 *Информация о {ticker}:*\n"
        f"• Загружено данных: {len(prices)} дней\n"
        f"• Текущая цена: ${current_price:.2f}\n"
        f"• Минимум: ${float(np.min(prices)):.2f}\n"
        f"• Максимум: ${float(np.max(prices)):.2f}\n\n"
        f"💵 *Введите сумму для инвестиции ($):*",
        parse_mode='Markdown'
    )
    
    await UserState.waiting_amount.set()

# ========== ОБРАБОТКА СУММЫ ==========

@dp.message_handler(state=UserState.waiting_amount)
async def process_amount(message: types.Message, state: FSMContext):
    """Обработка введенной суммы инвестиции"""
    try:
        # Парсим сумму
        amount_text = message.text.strip().replace(',', '.')
        amount = float(amount_text)
        
        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной!")
            return
        
        if amount > 1000000:
            await message.answer("⚠️ Для учебного проекта ограничение: $1,000,000")
            return
        
        # Получаем данные из состояния
        user_data = await state.get_data()
        ticker = user_data.get('ticker')
        prices = user_data.get('prices')
        
        if prices is None:
            await message.answer("❌ Данные не найдены. Начните заново /start")
            await state.finish()
            return
        
        print(f"[BOT] Анализ {ticker}, данных: {len(prices)}, сумма: ${amount}")
        
        # Начинаем анализ
        status_msg = await message.answer(
            "🔍 *Начинаю анализ...*\n\n"
            "Этапы:\n"
            "1. Подготовка данных ✓\n"
            "2. Обучение моделей...\n"
            "3. Построение прогноза...\n"
            "4. Формирование рекомендаций...",
            parse_mode='Markdown'
        )
        
        # ========== ПОДГОТОВКА ДАННЫХ ==========
        if len(prices) < 50:
            await message.answer("❌ Недостаточно данных для анализа")
            await state.finish()
            return
        
        # Разделяем данные
        split_idx = int(len(prices) * 0.8)
        train_data = prices[:split_idx]
        test_data = prices[split_idx:]
        
        print(f"[ANALYSIS] Данные: всего={len(prices)}, train={len(train_data)}, test={len(test_data)}")
        
        # ========== ОБУЧЕНИЕ МОДЕЛЕЙ ==========
        await status_msg.edit_text(
            "🔍 *Анализ...*\n\n"
            "Этапы:\n"
            "1. Подготовка данных ✓\n"
            "2. Обучение моделей ✓\n"
            "3. Построение прогноза...\n"
            "4. Формирование рекомендаций...",
            parse_mode='Markdown'
        )
        
        # Обучаем модели
        best_model_name, metrics = model_selector.train_and_evaluate(train_data, test_data)
        
        # ========== ПОСТРОЕНИЕ ПРОГНОЗА ==========
        await status_msg.edit_text(
            "🔍 *Анализ...*\n\n"
            "Этапы:\n"
            "1. Подготовка данных ✓\n"
            "2. Обучение моделей ✓\n"
            "3. Построение прогноза ✓\n"
            "4. Формирование рекомендаций...",
            parse_mode='Markdown'
        )
        
        # Делаем прогноз
        last_values = list(prices[-30:]) if len(prices) >= 30 else list(prices)
        forecast = model_selector.best_model.predict(last_values, steps=30)
        
        print(f"[ANALYSIS] Прогноз создан: {len(forecast)} дней")
        
        # ========== ВИЗУАЛИЗАЦИЯ ==========
        plot_buffer = visualizer.create_forecast_plot(prices[-100:], forecast, ticker)
        
        # ========== ИНВЕСТИЦИОННЫЕ РЕКОМЕНДАЦИИ ==========
        await status_msg.edit_text(
            "🔍 *Анализ...*\n\n"
            "Этапы:\n"
            "1. Подготовка данных ✓\n"
            "2. Обучение моделей ✓\n"
            "3. Построение прогноза ✓\n"
            "4. Формирование рекомендаций ✓",
            parse_mode='Markdown'
        )
        
        # Создаем стратегию
        strategy = strategy_module(forecast, amount)
        profit = strategy.calculate_profit()
        recommendations = strategy.generate_recommendations()
        
        # ========== ФОРМИРОВАНИЕ ОТВЕТА ==========
        current_price = float(prices[-1])
        forecast_price = float(forecast[-1])
        change_percent = ((forecast_price - current_price) / current_price) * 100
        
        response = (
            f"📊 *РЕЗУЛЬТАТЫ АНАЛИЗА {ticker}*\n"
            f"{'='*40}\n\n"
            
            f"📈 *ЦЕНЫ:*\n"
            f"• Текущая: ${current_price:.2f}\n"
            f"• Прогноз (30 дней): ${forecast_price:.2f}\n"
            f"• Изменение: {change_percent:+.1f}%\n\n"
            
            f"🤖 *МОДЕЛЬ:*\n"
            f"• Использована: {best_model_name}\n"
            f"• Точность (RMSE): ${metrics[best_model_name]['RMSE']:.2f}\n\n"
            
            f"💰 *ИНВЕСТИЦИИ:*\n"
            f"• Сумма: ${amount:.2f}\n"
            f"• Потенциальная прибыль: ${float(profit):.2f}\n"
            f"• Процент прибыли: {(float(profit)/amount*100):+.1f}%\n\n"
            
            f"🎯 *РЕКОМЕНДАЦИИ:*\n"
            f"{recommendations}\n\n"
            
            f"📅 *СРОКИ АНАЛИЗА:*\n"
            f"• Данных: {len(prices)} дней\n"
            f"• Прогноз на: 30 дней\n"
            f"• Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            
            f"⚠️ *УЧЕБНЫЙ ПРИМЕР*\n"
            f"Не является финансовой рекомендацией"
        )
        
        # ========== ОТПРАВКА РЕЗУЛЬТАТОВ ==========
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=plot_buffer,
            caption=response,
            parse_mode='Markdown'
        )
        
        # ========== ЛОГИРОВАНИЕ ==========
        app_logger.log_request(
            user_id=message.from_user.id,
            ticker=ticker,
            amount=amount,
            best_model=best_model_name,
            metrics=metrics.get(best_model_name, {}),
            profit=profit
        )
        
        await status_msg.delete()
        
        # Финальное сообщение
        await message.answer(
            "💡 *Для нового анализа введите /start*\n\n"
            "Хотите попробовать другой тикер?",
            parse_mode='Markdown'
        )
        
        await state.finish()
        
    except ValueError:
        await message.answer(
            "❌ Неверный формат суммы!\n"
            "Введите число (например: 1000 или 1500.50):"
        )
    except Exception as e:
        print(f"[ERROR] Ошибка в process_amount: {e}")
        import traceback
        traceback.print_exc()
        
        await message.answer(
            f"❌ Произошла ошибка при анализе\n"
            f"Попробуйте еще раз или выберите другой тикер.\n\n"
            f"Ошибка: `{str(e)[:100]}`",
            parse_mode='Markdown'
        )
        await state.finish()

# ========== ОБРАБОТКА ДРУГИХ СООБЩЕНИЙ ==========

@dp.message_handler()
async def handle_unknown(message: types.Message):
    """Обработка других сообщений"""
    if message.text:
        await message.answer(
            f"🤔 Я не понял команду \"{message.text}\"\n\n"
            f"Доступные команды:\n"
            f"• /start - Начать анализ акций\n"
            f"• /status - Проверить статус бота\n"
            f"• /help - Помощь\n\n"
            f"Или просто введите тикер акции для анализа"
        )

# ========== ЗАПУСК БОТА ==========

async def on_startup(_):
    """Действия при запуске"""
    print("\n" + "="*60)
    print("✅ Бот успешно запущен и готов к работе!")
    print("="*60 + "\n")
    
    # Создаем необходимые директории
    os.makedirs('logs', exist_ok=True)
    
    print("📁 Структура проекта:")
    print("├── bot_complete.py      (этот файл)")
    print("├── data_loader.py       (загрузка данных)")
    print("├── model_selector.py    (модели машинного обучения)")
    print("├── visualization.py     (графики)")
    print("├── strategy.py          (инвестиционные стратегии)")
    print("├── logger.py           (логирование)")
    print("└── logs/               (логи запросов)")
    print("\n🚀 Бот запущен! Откройте Telegram и начните работу.")

if __name__ == '__main__':
    try:
        print("🚀 Запуск polling...")
        executor.start_polling(
            dp,
            skip_updates=True,
            on_startup=on_startup,
            timeout=60
        )
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        print("\n👋 Бот завершил работу")
