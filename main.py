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
    return "<b>Premium Facebook Bot is Online!</b>"

def run_web_server():
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"Web Server Error: {e}")

def keep_alive():
    t = threading.Thread(target=run_web_server)
    t.start()

# ==================== BOT CONFIGURATION ====================
BOT_TOKEN = "8994561198:AAFUdohzb_82v_vdnYFcORdKuGOuQ5Vy-DQ"
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

# ==================== PREMIUM UI DESIGN ====================
MAIN_BTN_TEXT = "🟦   𝗚𝗘𝗧 𝗙𝗔𝗖𝗘𝗕𝗢𝗢𝗞 𝗡𝗨𝗠𝗕𝗘𝗥   🟦"
ADMIN_BTN_TEXT = "⚙️   𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟   ⚙️"

def premium_msg(title, body):
    """বোল্ড এবং প্রিমিয়াম লুক মেসেজ জেনারেটর"""
    msg = f"<b>💎 ━━━━━━━━━━━━━━ 💎</b>\n"
    msg += f"<b>👑 {title} 👑</b>\n"
    msg += f"<b>━━━━━━━━━━━━━━</b>\n\n"
    msg += f"<b>{body}</b>\n\n"
    msg += f"<b>💎 ━━━━━━━━━━━━━━ 💎</b>"
    return msg

# ==================== CORE API LOGIC ====================

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
                    country = log.get('country', 'Unknown')
                    r_val = log.get('range')
                    if country and r_val:
                        found_ranges[country] = r_val
                        if len(found_ranges) >= 15: break
    except: pass
    return found_ranges

# ==================== BOT HANDLERS ====================

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.chat.id
    
    # মেইন রিপ্লাই বাটন
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton(MAIN_BTN_TEXT))
    if uid == ADMIN_ID:
        markup.add(types.KeyboardButton(ADMIN_BTN_TEXT))
    
    welcome_body = (
        f"👋 𝗛𝗲𝗹𝗹𝗼 {message.from_user.first_name}!\n\n"
        "𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗼𝘂𝗿 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗙𝗮𝗰𝗲𝗯𝗼𝗼𝗸 𝗦𝗠𝗦 𝗦𝗲𝗿𝘃𝗶𝗰𝗲.\n"
        "𝗚𝗲𝘁 𝗵𝗶𝗴𝗵-𝗾𝘂𝗮𝗹𝗶𝘁𝘆 𝗻𝘂𝗺𝗯𝗲𝗿𝘀 𝗶𝗻𝘀𝘁𝗮𝗻𝘁𝗹𝘆."
    )
    # এখানে ভুল ছিল, সংশোধন করা হয়েছে
    bot.send_message(uid, premium_msg("𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", welcome_body), reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text_commands(message):
    uid = message.chat.id
    text = message.text

    if "GET" in text.upper() and "NUMBER" in text.upper():
        bot.send_chat_action(uid, 'typing')
        bot.send_message(uid, "<b>🔎 𝗦𝗲𝗮𝗿𝗰𝗵𝗶𝗻𝗴 𝗟𝗶𝘃𝗲 𝗦𝘁𝗼𝗰𝗸... 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁.</b>", parse_mode="HTML")
        
        ranges = get_live_facebook_ranges()
        if not ranges:
            bot.send_message(uid, premium_msg("𝗡𝗢 𝗦𝗧𝗢𝗖𝗞", "⚠️ 𝗡𝗼 𝗹𝗶𝘃𝗲 𝗙𝗮𝗰𝗲𝗯𝗼𝗼𝗸 𝗿𝗮𝗻𝗴𝗲𝘀 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗽𝗮𝗻𝗲𝗹 𝗿𝗶𝗴𝗵𝘁 𝗻𝗼𝘄."))
            return

        markup = types.InlineKeyboardMarkup(row_width=1)
        for country, rcode in ranges.items():
            btn_label = f"📘   {country.upper()}  ({rcode[:3]})   📘"
            markup.add(types.InlineKeyboardButton(btn_label, callback_data=f"buyfb_{rcode[:6]}_{country}"))
        
        bot.send_message(uid, premium_msg("𝗦𝗘𝗟𝗘𝗖𝗧 𝗖𝗢𝗨𝗡𝗧𝗥𝗬", "𝗖𝗵𝗼𝗼𝘀𝗲 𝗮 𝗹𝗶𝘃𝗲 𝗰𝗼𝘂𝗻𝘁𝗿𝘆 𝗳𝗿𝗼𝗺 𝗯𝗲𝗹𝗼𝘄:"), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.message.chat.id
    token = get_auth_token()

    if call.data.startswith("buyfb_"):
        parts = call.data.split("_")
        prefix, country = parts[1], parts[2]
        
        headers = {"mauthtoken": token, "Content-Type": "application/json"}
        payload = {"range": f"{prefix}XXXX", "is_national": False, "remove_plus": False}
        
        bot.edit_message_text(premium_msg("⏳ 𝗣𝗥𝗢𝗖𝗘𝗦𝗦𝗜𝗡𝗚", f"𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗶𝗻𝗴 {country} 𝗻𝘂𝗺𝗯𝗲𝗿..."), uid, call.message.message_id)
        
        try:
            resp = session.post(BUY_NUMBER_URL, json=payload, headers=headers, timeout=10)
            res = resp.json()
            if res.get('meta', {}).get('status') == "success":
                num = res['data']['full_number']
                
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("🔄   𝗖𝗛𝗔𝗡𝗚𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", callback_data=f"buyfb_{prefix}_{country}"),
                    types.InlineKeyboardButton("🔙   𝗕𝗔𝗖𝗞 𝗧𝗢 𝗠𝗘𝗡𝗨", callback_data="close")
                )
                
                res_body = (
                    f"✅ 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗!\n\n"
                    f"📞 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{num}</code>\n"
                    f"🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country}\n\n"
                    "📌 𝗦𝘂𝗯𝗺𝗶𝘁 𝗼𝗻 𝗙𝗮𝗰𝗲𝗯𝗼𝗼𝗸 𝗮𝗻𝗱 𝘄𝗮𝗶𝘁 𝗳𝗼𝗿 𝗢𝗧𝗣."
                )
                bot.edit_message_text(premium_msg("𝗡𝗨𝗠𝗕𝗘𝗥 𝗗𝗘𝗧𝗔𝗜𝗟𝗦", res_body), uid, call.message.message_id, reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "❌ No stock for this range!", show_alert=True)
                bot.edit_message_text(premium_msg("𝗦𝗧𝗢𝗖𝗞 𝗢𝗨𝗧", "𝗧𝗵𝗶𝘀 𝗰𝗼𝘂𝗻𝘁𝗿𝘆 𝗶𝘀 𝗼𝘂𝘁 𝗼𝗳 𝘀𝘁𝗼𝗰𝗸. 𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 𝗮𝗻𝗼𝘁𝗵𝗲𝗿."), uid, call.message.message_id)
        except:
            bot.answer_callback_query(call.id, "❌ Connection Error!")

    elif call.data == "close":
        bot.delete_message(uid, call.message.message_id)

# ==================== RUN BOT ====================
if __name__ == "__main__":
    print("🚀 Premium Blue Facebook Bot is Starting...")
    keep_alive()
    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=10)
    except Exception as e:
        print(f"Polling Error: {e}")
        time.sleep(5)
