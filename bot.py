import os
import time
import telebot
from openai import OpenAI

# Read tokens from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8345014638:AAFDK_WxUO21bhMxcNOFCrGwdJbPY1_XDlQ"
OPENAI_KEY = os.getenv("OPENAI_KEY") or "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"

if not BOT_TOKEN or not OPENAI_KEY:
    raise RuntimeError("BOT_TOKEN and OPENAI_KEY must be set")

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_KEY)

# Per-user conversation history: chat_id -> list of messages
conversations = {}

def detect_gender(name: str) -> str:
    if not name:
        return "male"
    name = name.lower()
    if name.endswith(("а", "я")):
        return "female"
    return "male"

def get_bot_name(user_gender: str) -> str:
    return "Алина" if user_gender == "male" else "Иван"

def ask_openai(user_id: int, user_name: str, bot_name: str, user_text: str) -> str:
    history = conversations.setdefault(user_id, [])
    if not history:
        system_prompt = (
            f"Ты {bot_name}, весёлый и дружелюбный собеседник. "
            "Общайся непринуждённо, с юмором и эмодзи, как реальный человек. "
            "Всегда обращайся к собеседнику по имени."
        )
        history.append({"role": "system", "content": system_prompt})
    history.append({"role": "user", "content": f"{user_name}: {user_text}"})
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history,
    )
    reply = completion.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    if len(history) > 20:
        del history[1:3]
    return reply

@bot.message_handler(func=lambda _: True)
def handle_message(message):
    user_name = message.from_user.first_name or "друг"
    user_id = message.chat.id
    gender = detect_gender(user_name)
    bot_name = get_bot_name(gender)

    bot.send_chat_action(user_id, "typing")
    time.sleep(1.5)

    reply = ask_openai(user_id, user_name, bot_name, message.text)
    bot.reply_to(message, reply)

if __name__ == "__main__":
    print("🤖 Бот запущен и готов к дружескому общению!")
    bot.polling()


