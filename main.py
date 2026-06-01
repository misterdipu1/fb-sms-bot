import telebot
import requests
import threading
import time
import re
from flask import Flask
from telebot import types
from datetime import datetime, timedelta

# ==================== KEEP ALIVE SERVER ====================
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run_web_server)
    t.start()
# ===========================================================

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8994561198:AAG2CspmFsjnp9erAx1EgbBXZYSTAH-_eaU"
ADMIN_ID = 6903748951
GMAIL = "sojibsorkar388@gmail.com"
PASSWORD = "Sojib098@#"

BASE_URL = "https://stexsms.com/mapi/v1"
LOGIN_URL = f"{BASE_URL}/mauth/login"
LIVE_RANGE_URL = f"{BASE_URL}/mdashboard/console/info"
BUY_NUMBER_URL = f"{BASE_URL}/mdashboard/getnum/number"
ORDER_INFO_URL = f"{BASE_URL}/mdashboard/getnum/info"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
session = requests.Session()
AUTH_TOKEN = None

# UI DESIGN
MAIN_BTN_TEXT = "🟦   𝗚𝗘𝗧 𝗙𝗔𝗖𝗘𝗕𝗢𝗢Ｋ 𝗡𝗨𝗠Ｂ𝗘𝗥   🟦"
ADMIN_BTN_TEXT = "⚙️   𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟"

def get_auth_token():
    global AUTH_TOKEN
    payload = {"email": GMAIL, "password": PASSWORD}
    try:
        resp = session.post(LOGIN_URL, json=payload, timeout=10)
        data = resp.json()
        if data.get('meta', {}).get('status') == 'success':
            return data['data']['token']
    except: return None

def get_live_facebook_ranges():
    token = get_auth_token()
    if not token: return {}
    headers = {"mauthtoken": token}
    found_ranges = {}
    try:
        resp = session.get(LIVE_RANGE_URL, headers=headers, timeout=12)
        data = resp.json()
        if data.get('data') and 'logs' in data['data']:
            for log in data['data']['logs']:
                if not log: continue
                app = str(log.get('app_name', '')).lower()
                if 'facebook' in app or 'fb' in app:
                    country = log.get('country')
                    r_val = log.get('range')
                    if country and r_val: found_ranges[country] = r_val
    except: pass
    return found_ranges

def premium_msg(title, body):
    return f"<b>💎 ━━━━━━━━━━━━━━ 💎\n👑 {title} 👑\n━━━━━━━━━━━━━━\n\n{body}\n\n💎 ━━━━━━━━━━━━━━ 💎</b>"

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton(MAIN_BTN_TEXT))
    if message.chat.id == ADMIN_ID:
        markup.add(types.KeyboardButton(ADMIN_BTN_TEXT))
    bot.send_message(message.chat.id, premium_msg("𝗙𝗔𝗖𝗘𝗕𝗢𝗢𝗞 𝗕𝗢𝗧", "𝗪𝗲𝗹𝗰𝗼𝗺𝗲! 𝗖𝗹𝗶𝗰𝗸 𝘁𝗵𝗲 𝗯𝗹𝘂𝗲 𝗯𝘂𝘁𝘁𝗼𝗻 𝘁𝗼 𝘀𝘁𝗮𝗿𝘁."), reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text_buttons(message):
    if message.text == MAIN_BTN_TEXT:
        ranges = get_live_facebook_ranges()
        if not ranges:
            bot.send_message(message.chat.id, premium_msg("𝗡𝗢 𝗦𝗧𝗢𝗖𝗞", "⚠️ 𝗡𝗼 𝗹𝗶𝘃𝗲 𝗙𝗮𝗰𝗲𝗯𝗼𝗼𝗸 𝗿𝗮𝗻𝗴𝗲𝘀 found."))
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for country, rcode in ranges.items():
            markup.add(types.InlineKeyboardButton(f"📘   {country.upper()}  ({rcode[:3]})   📘", callback_data=f"buyfb_{rcode[:6]}_{country}"))
        bot.send_message(message.chat.id, premium_msg("𝗦𝗘𝗟𝗘𝗖𝗧 𝗖𝗢𝗨𝗡𝗧𝗥𝗬", "𝗖𝗵𝗼𝗼𝘀𝗲 𝗮 𝗰𝗼𝘂𝗻𝘁𝗿𝘆:"), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.message.chat.id
    if call.data.startswith("buyfb_"):
        parts = call.data.split("_")
        prefix, country = parts[1], parts[2]
        token = get_auth_token()
        headers = {"mauthtoken": token, "Content-Type": "application/json"}
        payload = {"range": f"{prefix}XXXX", "is_national": False, "remove_plus": False}
        bot.edit_message_text(premium_msg("⏳ 𝗣𝗥𝗢𝗖𝗘𝗦𝗦𝗜𝗡𝗚", f"𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗶𝗻𝗴 {country} 𝗻𝘂𝗺𝗯𝗲𝗿..."), uid, call.message.message_id)
        try:
            resp = session.post(BUY_NUMBER_URL, json=payload, headers=headers)
            res = resp.json()
            if res.get('meta', {}).get('status') == "success":
                num = res['data']['full_number']
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(types.InlineKeyboardButton("🔄   𝗖𝗛𝗔𝗡𝗚𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", callback_data=f"buyfb_{prefix}_{country}"))
                bot.edit_message_text(premium_msg("✅ 𝗡𝗨𝗠𝗕𝗘𝗥 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗", f"📞 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{num}</code>\n\n𝗦𝘂𝗯𝗺𝗶𝘁 𝗼𝗻 𝗙𝗮𝗰𝗲𝗯𝗼𝗼𝗸."), uid, call.message.message_id, reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "❌ Stock Out!", show_alert=True)
        except: pass

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
