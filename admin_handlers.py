from telebot import types
import config
import database
import telebot

conn = database.connect_db()
cursor = conn.cursor()

admin_mode = {}
product_step = {}
products = {}
users_page = {}

# Добавление функции для показа пользователей с пагинацией
def show_users_page(bot, chat_id, page_number):
    conn = database.connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    if total_users == 0:
        bot.send_message(chat_id, "Пользователей нет.")
        return

    cursor.execute('SELECT id, username, first_name, balance, total_topups, total_purchases FROM users LIMIT 10 OFFSET ?', ((page_number - 1) * 10,))
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    users_info = "\n\n".join([
        f"🆔ID: {escape_markdown(str(user[0]))}\n👤 Юзернейм: @{escape_markdown(str(user[1]))}\n📛 Имя: {escape_markdown(str(user[2]))}\n💰 Баланс: {user[3]:.2f} руб\n💸 Сумма пополнений: {user[4]:.2f} руб\n🛒 Количество покупок: {user[5]}"
        for user in users
    ])

    markup = types.InlineKeyboardMarkup()
    if page_number > 1:
        markup.add(types.InlineKeyboardButton(text="⏪ Влево", callback_data=f'users_page_{page_number - 1}'))
    if (page_number * 10) < total_users:
        markup.add(types.InlineKeyboardButton(text="⏩ Вправо", callback_data=f'users_page_{page_number + 1}'))

    bot.send_message(chat_id, f"Количество пользователей: {total_users}\n\n{users_info}", reply_markup=markup, parse_mode='Markdown')

def escape_markdown(text):
    escape_chars = r'\*_`['
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def send_main_menu(bot, chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    profile_button = types.KeyboardButton("👤 Профиль")
    products_button = types.KeyboardButton("🛍️ Товары")
    markup.add(profile_button, products_button)
    bot.send_message(chat_id, "Вы в главном меню.", reply_markup=markup)

def setup_admin_handlers(bot):
    @bot.message_handler(commands=['admin'])
    def admin_panel(message):
        if message.from_user.id == config.ADMIN_ID:
            admin_mode[message.from_user.id] = True
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            broadcast_button = types.KeyboardButton("📢 Рассылка")
            change_balance_button = types.KeyboardButton("💰 Изменить баланс")
            user_count_button = types.KeyboardButton("👥 Количество пользователей")
            add_product_button = types.KeyboardButton("➕ Добавить товар")
            delete_product_button = types.KeyboardButton("❌ Удалить товар")
            edit_product_button = types.KeyboardButton("✏️ Редактировать товар")
            exit_button = types.KeyboardButton("❌ Выйти")
            markup.add(broadcast_button, change_balance_button, user_count_button, add_product_button, delete_product_button, edit_product_button, exit_button)
            bot.send_message(message.chat.id, "Админ панель:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")

    @bot.message_handler(commands=['off'])
    def exit_admin_panel(message):
        if message.from_user.id in admin_mode:
            del admin_mode[message.from_user.id]
        send_main_menu(bot, message.chat.id)
        bot.send_message(message.chat.id, "Вы вышли из админ панели.")

    @bot.message_handler(func=lambda message: message.from_user.id in admin_mode)
    def admin_actions(message):
        chat_id = message.chat.id
        
        if message.text == "📢 Рассылка":
            bot.send_message(chat_id, "Введите текст для рассылки:")
            bot.register_next_step_handler(message, broadcast_message)
            
        elif message.text == "💰 Изменить баланс":
            bot.send_message(chat_id, "Введите ID пользователя, чей баланс вы хотите изменить:")
            bot.register_next_step_handler(message, get_user_balance)
        elif message.text == "👥 Количество пользователей":
            users_page[chat_id] = 1
            show_users_page(bot, chat_id, users_page[chat_id])

        elif message.text == "➕ Добавить товар":
            bot.send_message(chat_id, "Введите имя товара:")
            bot.register_next_step_handler(message, process_product_name)
    
        elif message.text == "❌ Удалить товар":
            cursor.execute('SELECT * FROM products')
            product_list = cursor.fetchall()
            if not product_list:
                bot.send_message(chat_id, "Товаров нет.")
                return

            markup = types.InlineKeyboardMarkup()
            for product in product_list:
                markup.add(types.InlineKeyboardButton(text=product[1], callback_data=f'delete_product_{product[0]}'))
            bot.send_message(chat_id, "Выберите товар для удаления:", reply_markup=markup)

        elif message.text == "✏️ Редактировать товар":
            select_product_to_edit(message)

        elif message.text == "❌ Выйти":
            exit_admin_panel(message)
        
        else:
            bot.send_message(message.chat.id, "Неизвестная команда. Пожалуйста, выберите одну из опций.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('users_page_'))
    def change_users_page(call):
        page_number = int(call.data.split('_')[2])
        users_page[call.message.chat.id] = page_number
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_users_page(bot, call.message.chat.id, page_number)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('delete_product_'))
    def delete_product(call):
        product_id = int(call.data.split('_')[2])
        
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        
        bot.send_message(call.message.chat.id, "Товар успешно удален.")
    
    # Определение функции select_product_to_edit
    def select_product_to_edit(message):
        cursor.execute('SELECT * FROM products')
        product_list = cursor.fetchall()
        if not product_list:
            bot.send_message(message.chat.id, "Товаров нет.")
            return

        markup = types.InlineKeyboardMarkup()
        for product in product_list:
          markup.add(types.InlineKeyboardButton(product[1], callback_data=f"edit_{product[0]}"))
