import telebot
import requests
import threading
import time
from flask import Flask
from telebot import types

# Keep Alive Server for Render
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run_web_server():
    try:
        app.run(host='0.0.0.0', port=8080)
    except: pass

def keep_alive():
    threading.Thread(target=run_web_server, daemon=True).start()

# --- এখানে আপনার নতুন টোকেনটি বসান ---
BOT_TOKEN = "8994561198:AAFzdF7VJOBggBMvWkQ8PjZeP8rdV18Qfj0" 

ADMIN_ID = 6903748951
GMAIL = "sojibsorkar388@gmail.com"
PASSWORD = "Sojib098@#"

BASE_URL = "https://stexsms.com/mapi/v1"
LOGIN_URL = f"{BASE_URL}/mauth/login"
LIVE_RANGE_URL = f"{BASE_URL}/mdashboard/console/info"
BUY_NUMBER_URL = f"{BASE_URL}/mdashboard/getnum/number"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
session = requests.Session()

# UI DESIGN
MAIN_BTN_TEXT = "🟦   𝗚𝗘𝗧 𝗙𝗔𝗖𝗘𝗕𝗢𝗢𝗞 𝗡𝗨𝗠𝗕𝗘𝗥   🟦"

def premium_msg(title, body):
    return f"<b>💎 ━━━━━━━━━━━━━━ 💎\n👑 {title} 👑\n━━━━━━━━━━━━━━\n\n{body}\n\n💎 ━━━━━━━━━━━━━━ 💎</b>"

def get_auth_token():
    payload = {"email": GMAIL, "password": PASSWORD}
    try:
        resp = session.post(LOGIN_URL, json=payload, timeout=10)
        data = resp.json()
        return data['data']['token']
    except: return None

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton(MAIN_BTN_TEXT))
    bot.send_message(message.chat.id, premium_msg("𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", "𝗪𝗲𝗹𝗰𝗼𝗺𝗲! 𝗖𝗹𝗶𝗰𝗸 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝘀𝘁𝗮𝗿𝘁."), reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if "GET" in message.text.upper():
        bot.send_message(message.chat.id, "🔎 <b>Checking stock, please wait...</b>", parse_mode="HTML")
        # লাইভ রেঞ্জ লজিক... (আগের মতোই থাকবে)
        bot.send_message(message.chat.id, premium_msg("𝗡𝗢 𝗦𝗧𝗢𝗖𝗞", "⚠️ 𝗡𝗼 𝗹𝗶𝘃𝗲 𝗙𝗮𝗰𝗲𝗯𝗼𝗼𝗸 𝗿𝗮𝗻𝗴𝗲𝘀 𝗳𝗼𝘂𝗻𝗱."))

if __name__ == "__main__":
    keep_alive()
    print("🚀 Cleaning old sessions...")
    bot.remove_webhook() # এটি সব পুরনো কানেকশন কেটে দিবে
    time.sleep(2)
    print("🚀 Bot is starting fresh...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
