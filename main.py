from telebot import TeleBot, types
import config
import admin_handlers
import profile_handlers
import payment_handlers

bot = TeleBot(config.TOKEN)

# Подключаем обработчики из других файлов
admin_handlers.setup_admin_handlers(bot)
profile_handlers.setup_profile_handlers(bot)
payment_handlers.setup_payment_handlers(bot)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Проверяем, является ли пользователь администратором
    if user_id == config.ADMIN_ID:
        # Клавиатура для администратора
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton("🛍 Каталог"),
            types.KeyboardButton("💰 Баланс"),
            types.KeyboardButton("📞 Поддержка")
        )
        markup.add(types.KeyboardButton("📊 Админ-панель"))
        
        bot.send_message(
            message.chat.id,
            f"👋 Привет, администратор {first_name}!\n"
            f"Добро пожаловать в панель управления магазином.",
            reply_markup=markup
        )
    else:
        # Клавиатура для обычного пользователя
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton("🛍 Каталог"),
            types.KeyboardButton("💰 Баланс"),
            types.KeyboardButton("📞 Поддержка")
        )
        
        bot.send_message(
            message.chat.id,
            f"👋 Привет, {first_name}!\n"
            f"Добро пожаловать в магазин аккаунтов!\n\n"
            f"Используй кнопки ниже для навигации.",
            reply_markup=markup
        )

# Обработчик текстовых сообщений (для кнопок)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    
    if message.text == "🛍 Каталог":
        bot.send_message(message.chat.id, "Раздел каталога в разработке")
    
    elif message.text == "💰 Баланс":
        bot.send_message(message.chat.id, f"💰 Твой баланс: 0 руб.")
    
    elif message.text == "📞 Поддержка":
        bot.send_message(
            message.chat.id,
            "📞 Связь с поддержкой: @username\n"
            "Время ответа: в течение дня"
        )
    
    elif message.text == "📊 Админ-панель" and user_id == config.ADMIN_ID:
        bot.send_message(message.chat.id, "Админ-панель в разработке")
    
    else:
        bot.send_message(message.chat.id, "Используй кнопки меню для навигации.")

# Команда для получения своего ID
@bot.message_handler(commands=['myid'])
def myid(message):
    bot.send_message(
        message.chat.id,
        f"🆔 Твой Telegram ID: {message.from_user.id}",
        parse_mode='Markdown'
    )

# Команда для проверки работы бота
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.send_message(message.chat.id, "pong 🏓")

# ЭТО САМОЕ ГЛАВНОЕ - ПРАВИЛЬНАЯ КОНСТРУКЦИЯ!
if name == 'main':
    print("✅ Бот запущен и готов к работе!")
    bot.polling(non_stop=True)
