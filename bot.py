import telebot
from telebot import types
import json

# === НАСТРОЙКИ ===
TOKEN = '8785656463:AAEcl9GU-fRkmcZiWk7dFbCpjWOG0hkmMx8'
GROUP_ID = -1003994862974  # ID твоей группы
WEB_APP_URL = 'https://kazbala6-png.github.io/ninja-shop/'  # Твоя ссылка на GitHub Pages

bot = telebot.TeleBot(TOKEN)

# --- Функция создания клавиатуры ---
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    web_app_info = types.WebAppInfo(WEB_APP_URL)
    btn_shop = types.KeyboardButton(" Открыть Каталог", web_app=web_app_info)
    btn_info = types.KeyboardButton(" Адрес и Доставка")
    btn_support = types.KeyboardButton(" Написать менеджеру")
    
    markup.add(btn_shop)
    markup.add(btn_info, btn_support)
    return markup

# --- 1. КОМАНДА /start ---
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = (
        f"Салам, {message.from_user.first_name}! \n\n"
        "Добро пожаловать в CLOTHING STORE!\n\n"
        "Нажимай кнопку « Открыть Каталог» ниже, чтобы выбрать вещи и оформить заявку."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# --- 2. ОБРАБОТКА ТЕКСТОВЫХ КНОПОК ---
@bot.message_handler(func=lambda message: message.text == " Адрес и Доставка")
def send_address_info(message):
    text = (
        " Офлайн точка: г. Актобе, ТРЦ / Улица Примерная, 10\n"
        " Режим работы: Каждый день с 10:00 до 21:00\n\n"
        " Варианты получения:\n"
        "• Самовывоз из магазина\n"
        "• Экспресс-доставка по Актобе (Яндекс.Такси / Курьер)\n"
        "• Доставка по Казахстану (Казпочта / CDEK)"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == " Написать менеджеру")
def send_support_info(message):
    text = (
        " Связь с менеджером:\n\n"
        "Если у тебя есть вопросы по наличию, размерам или доставке — напиши напрямую менеджеру: @peruza45\n\n"
        "Мы ответим в течение нескольких минут!"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# --- 3. ПРИЕМ ЗАКАЗА ИЗ WEB APP (Витрины) ---
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        user = message.from_user
        
        user_info = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
        
        items_text = ""
        for item in data['items']:
            items_text += f"• {item['name']} | Размер: {item['size']} — {item['price']} ₸\n"
            if item.get('image'):
                items_text += f"  └ [Ссылка на фото товара]({item['image']})\n"

        # 1. Отправляем карточку в РАБОЧУЮ ГРУППУ
        group_message = (
            " НОВАЯ ЗАЯВКА ИЗ ВИТРИНЫ!\n\n"
            f" Покупатель: {user_info}\n\n"
            f" Выбранный ассортимент:\n{items_text}\n"
            f" Общая сумма: {data['totalPrice']} ₸"
        )
        
        markup_group = types.InlineKeyboardMarkup()
        btn_reply = types.InlineKeyboardButton(" Ответить клиенту", url=f"tg://user?id={user.id}")
        markup_group.add(btn_reply)
        
        bot.send_message(GROUP_ID, group_message, parse_mode="Markdown", reply_markup=markup_group)

        # 2. Подтверждение КЛИЕНТУ в личку
        client_message = (
            " Ваша заявка успешно передана менеджеру!\n\n"
            f" Выбранные вещи:\n{items_text}\n"
            f" Предварительная сумма: {data['totalPrice']} ₸\n\n"
            " Наш менеджер свяжется с вами прямо в этом чате в течение 5 минут для уточнения деталей!"
        )
        bot.send_message(user.id, client_message, parse_mode="Markdown", reply_markup=get_main_keyboard())

    except Exception as e:
        print(f"Ошибка при обработке заказа: {e}")

print(" Бот обновлен и запущен!")
bot.infinity_polling()
