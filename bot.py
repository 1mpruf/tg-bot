import telebot
import google.generativeai as genai
import time

# 🔑 Твои ключи
BOT_TOKEN = "8345014638:AAFDK_WxUO21bhMxcNOFCrGwdJbPY1_XDlQ"
GEMINI_KEY = "AIzaSyAV6RgBdvlamJKCKyjiOjvR4rPeGz5NY2U"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# Модель Gemini с "живым" стилем
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=(
        "Ты живой человек, а не робот. Общайся дружелюбно, просто, с юмором, иногда добавляй эмодзи 😊🔥😉. "
        "Не используй сухой официозный стиль, будь естественным собеседником."
    ),
)

# Память диалогов: user_id -> ChatSession
conversations = {}

# Определение пола по имени
def detect_gender(name: str) -> str:
    if not name:
        return "male"
    name = name.lower()
    if name.endswith(("а", "я")):
        return "female"
    return "male"

# Имя бота в зависимости от пола юзера
def get_bot_name(user_gender: str) -> str:
    if user_gender == "male":
        return "Алина"   # если пишет парень, бот = девушка
    else:
        return "Иван"    # если пишет девушка, бот = парень

def ask_gemini(user_id: int, user_name: str, bot_name: str, user_text: str) -> str:
    chat = conversations.get(user_id)
    if chat is None:
        chat = model.start_chat()
        conversations[user_id] = chat
    try:
        response = chat.send_message(
            f"Собеседник {user_name} написал: {user_text}. Ты — {bot_name}. Ответь дружелюбно."
        )
        return response.text
    except Exception as e:
        return f"⚠️ Ошибка: {e}"

# Обработка всех сообщений
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    gender = detect_gender(user_name)
    bot_name = get_bot_name(gender)

    # Эффект "печатает..."
    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(2)  # задержка 2 секунды

    reply = ask_gemini(user_id, user_name, bot_name, message.text)
    bot.reply_to(message, reply)

print("✅ Бот с живым стилем и эффектом печати запущен!")
bot.polling()
