from telebot import TeleBot, types
import config
import sqlite3

bot = TeleBot(config.TOKEN)

# === База данных ===
conn = sqlite3.connect(config.DATABASE_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS products
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   price INTEGER)''')
conn.commit()

# === Клавиатуры ===
def user_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛍 Каталог", "💰 Баланс")
    markup.add("📞 Поддержка")
    return markup

def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Добавить товар", "❌ Удалить товар")
    markup.add("📋 Список товаров", "◀️ Выйти")
    return markup

# === Старт ===
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == config.ADMIN_ID:
        bot.send_message(message.chat.id, "👋 Привет, админ!", reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, "👋 Привет! Добро пожаловать в магазин.", reply_markup=user_keyboard())

# === Обработка кнопок ===
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    uid = message.from_user.id
    text = message.text

    # Пользовательские кнопки
    if text == "🛍 Каталог":
        cursor.execute("SELECT * FROM products")
        items = cursor.fetchall()
        if not items:
            bot.send_message(message.chat.id, "📭 Товаров пока нет.")
        else:
            for item in items:
                bot.send_message(message.chat.id, f"{item[1]} — {item[2]} руб.")

    elif text == "💰 Баланс":
        bot.send_message(message.chat.id, "💰 Ваш баланс: 0 руб. (функция в разработке)")

    elif text == "📞 Поддержка":
        bot.send_message(message.chat.id, "📞 Поддержка: @support")

    # Админ-кнопки
    elif uid == config.ADMIN_ID:
        if text == "➕ Добавить товар":
            msg = bot.send_message(message.chat.id, "Введите название товара:")
            bot.register_next_step_handler(msg, process_product_name)

        elif text == "❌ Удалить товар":
            cursor.execute("SELECT * FROM products")
            items = cursor.fetchall()
            if not items:
                bot.send_message(message.chat.id, "Нет товаров для удаления.")
                return
            markup = types.InlineKeyboardMarkup()
            for item in items:
                markup.add(types.InlineKeyboardButton(
                    text=item[1],
                    callback_data=f"del_{item[0]}"
                ))
            bot.send_message(message.chat.id, "Выберите товар для удаления:", reply_markup=markup)

        elif text == "📋 Список товаров":
            cursor.execute("SELECT * FROM products")
            items = cursor.fetchall()
            if not items:
                bot.send_message(message.chat.id, "Список пуст.")
            else:
                for item in items:
                    bot.send_message(message.chat.id, f"🆔 {item[0]}: {item[1]} — {item[2]} руб.")

        elif text == "◀️ Выйти":
            bot.send_message(message.chat.id, "Выход из админки.", reply_markup=user_keyboard())

# === Добавление товара ===
def process_product_name(message):
    name = message.text
    msg = bot.send_message(message.chat.id, "Введите цену товара (только число):")
    bot.register_next_step_handler(msg, process_product_price, name)

def process_product_price(message, name):
    try:
        price = int(message.text)
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        bot.send_message(message.chat.id, "✅ Товар добавлен!", reply_markup=admin_keyboard())
    except:
        bot.send_message(message.chat.id, "❌ Ошибка. Введите число.")

# === Удаление товара ===
@bot.callback_query_handler(func=lambda call: call.data.startswith('del_'))
def delete_product(call):
    pid = call.data.split('_')[1]
    cursor.execute("DELETE FROM products WHERE id = ?", (pid,))
    conn.commit()
    bot.answer_callback_query(call.id, "✅ Удалено")
    bot.delete_message(call.message.chat.id, call.message.message_id)

# === Запуск ===
if __name__ == '__main__':
    print("✅ Бот запущен")
    bot.polling(non_stop=True)
