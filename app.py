import os
import threading
from flask import Flask
import main  # ЭТО ТВОЙ ОСНОВНОЙ ФАЙЛ БОТА (main.py)

# Создаем Flask приложение
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/health')
def health():
    return "OK", 200

# Функция для запуска твоего бота в отдельном потоке
def run_bot():
    # Здесь просто вызывается твой бот
    # Предполагается, что в main.py есть бесконечный polling
    if hasattr(main, 'bot') and hasattr(main.bot, 'infinity_polling'):
        main.bot.infinity_polling()
    else:
        # Если структура другая - импортируй и запусти нужную функцию
        print("Бот запущен через main.py")

# Запускаем бота в фоне при старте
threading.Thread(target=run_bot, daemon=True).start()

if name == 'main':
    # Запускаем Flask на порту, который даст Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
