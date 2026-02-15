import telebot
from telebot import types
import config
import sqlite3

# Подключение к базе данных
conn = sqlite3.connect(config.DATABASE_NAME, check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы products, если её нет
cursor.execute('''CREATE TABLE IF NOT EXISTS products
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   price INTEGER,
                   description TEXT)''')
conn.commit()

# Словарь для хранения страниц пользователей
users_page = {}

def setup_admin_handlers(bot):
    
    def show_admin_panel(message):
        """Показывает админ-панель"""
        if message.from_user.id != config.ADMIN_ID:
            bot.send_message(message.chat.id, "У вас нет прав администратора.")
            return
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton("💰 Изменить баланс"),
            types.KeyboardButton("👥 Количество пользователей"),
            types.KeyboardButton("➕ Добавить товар"),
            types.KeyboardButton("❌ Удалить товар"),
            types.KeyboardButton("✏️ Редактировать товар"),
            types.KeyboardButton("❌ Выйти")
        )
        bot.send_message(message.chat.id, "🔧 Админ-панель\nВыберите действие:", reply_markup=markup)

    def show_users_page(bot, chat_id, page):
        """Показывает список пользователей по страницам"""
        # Здесь должна быть логика показа пользователей
        bot.send_message(chat_id, f"Страница {page} пользователей (функция в разработке)")

    def exit_admin_panel(message):
        """Выход из админ-панели"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton("🛍 Каталог"),
            types.KeyboardButton("💰 Баланс"),
            types.KeyboardButton("📞 Поддержка")
        )
        bot.send_message(message.chat.id, "Вы вышли из админ-панели.", reply_markup=markup)

    # Обработчик текстовых сообщений в админ-панели
    @bot.message_handler(func=lambda message: message.from_user.id == config.ADMIN_ID)
    def admin_commands(message):
        chat_id = message.chat.id
        
        if message.text == "💰 Изменить баланс":
            bot.send_message(chat_id, "Введите ID пользователя, чей баланс вы хотите изменить:")
            bot.register_next_step_handler(message, get_user_balance)
        
        elif message.text == "👥 Количество пользователей":
            users_page[chat_id] = 1
            show_users_page(bot, chat_id, users_page[chat_id])

        elif message.text == "➕ Добавить товар":
            bot.send_message(chat_id, "Введите название товара:")
            bot.register_next_step_handler(message, process_product_name)
    
        elif message.text == "❌ Удалить товар":
            cursor.execute('SELECT * FROM products')
            product_list = cursor.fetchall()
            if not product_list:
                bot.send_message(chat_id, "📭 Товаров нет.")
                return

            markup = types.InlineKeyboardMarkup()
            for product in product_list:
                button = types.InlineKeyboardButton(
                    text=f"{product[1]} (ID: {product[0]})", 
                    callback_data=f'delete_product_{product[0]}'
                )
                markup.add(button)
            bot.send_message(chat_id, "Выберите товар для удаления:", reply_markup=markup)

        elif message.text == "✏️ Редактировать товар":
            select_product_to_edit(message)

        elif message.text == "❌ Выйти":
            exit_admin_panel(message)
        
        else:
            bot.send_message(message.chat.id, "Неизвестная команда. Пожалуйста, выберите одну из опций.")
  # Обработчик для пагинации пользователей
    @bot.callback_query_handler(func=lambda call: call.data.startswith('users_page_'))
    def change_users_page(call):
        page_number = int(call.data.split('_')[2])
        users_page[call.message.chat.id] = page_number
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_users_page(bot, call.message.chat.id, page_number)
    
    # Обработчик для удаления товара
    @bot.callback_query_handler(func=lambda call: call.data.startswith('delete_product_'))
    def delete_product(call):
        product_id = int(call.data.split('_')[2])
        
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        
        bot.send_message(call.message.chat.id, "✅ Товар успешно удален.")
        bot.answer_callback_query(call.id)

    # Обработчик для выбора товара для редактирования
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
    def edit_product(call):
        product_id = int(call.data.split('_')[1])
        bot.send_message(call.message.chat.id, f"Редактирование товара ID {product_id} (функция в разработке)")
        bot.answer_callback_query(call.id)
    
    # Функция выбора товара для редактирования
    def select_product_to_edit(message):
        cursor.execute('SELECT * FROM products')
        product_list = cursor.fetchall()
        if not product_list:
            bot.send_message(message.chat.id, "📭 Товаров нет.")
            return

        markup = types.InlineKeyboardMarkup()
        for product in product_list:
            # ВАЖНО: правильный отступ - 4 пробела!
            button = types.InlineKeyboardButton(
                text=f"{product[1]} - {product[2]} руб.", 
                callback_data=f"edit_{product[0]}"
            )
            markup.add(button)
        
        # ОТПРАВЛЯЕМ сообщение с клавиатурой!
        bot.send_message(
            message.chat.id, 
            "✏️ Выберите товар для редактирования:", 
            reply_markup=markup
        )

    # Функция для изменения баланса (заглушка)
    def get_user_balance(message):
        user_id = message.text
        bot.send_message(message.chat.id, f"Функция изменения баланса для пользователя {user_id} в разработке.")

    # Функция для добавления товара (заглушка)
    def process_product_name(message):
        product_name = message.text
        bot.send_message(message.chat.id, f"Товар '{product_name}' будет добавлен (функция в разработке).")

    # Возвращаем функцию показа админ-панели для использования в main.py
    return show_admin_panel
