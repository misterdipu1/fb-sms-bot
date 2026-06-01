import telebot
import requests
import threading
import time
import re
from flask import Flask
from telebot import types
from datetime import datetime

# ==================== KEEP ALIVE SERVER ====================
app = Flask('')
@app.route('/')
def home(): return "<b>Premium Bot is Active!</b>"
def run_web_server():
    try: app.run(host='0.0.0.0', port=8080)
    except: pass
def keep_alive():
    threading.Thread(target=run_web_server, daemon=True).start()

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8994561198:AAG2CspmFsjnp9erAx1EgbBXZYSTAH-_eaU" 
ADMIN_ID = 6903748951
GMAIL = "sojibsorkar388@gmail.com"
PASSWORD = "Sojib098@#"

BASE_URL = "https://stexsms.com/mapi/v1"
LOGIN_URL = f"{BASE_URL}/mauth/login"
INFO_URL = f"{BASE_URL}/mdashboard/console/info"
BUY_URL = f"{BASE_URL}/mdashboard/getnum/number"
ORDER_URL = f"{BASE_URL}/mdashboard/getnum/info"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
session = requests.Session()
AUTH_TOKEN = None

# ইন-মেমোরি ডাটাবেজ
USER_BALANCES = {} # {user_id: balance}
MANUAL_RANGES = {"Ivory Coast 🇨🇮": "22507", "Bangladesh 🇧🇩": "88017", "India 🇮🇳": "919", "USA 🇺🇸": "1"}
USERS_DB = set()

# ==================== DESIGN HELPERS ====================
def premium_msg(title, body):
    msg = f"<b>💎 ━━━━━━━━━━━━━━ 💎\n👑 {title} 👑\n━━━━━━━━━━━━━━\n\n{body}\n\n💎 ━━━━━━━━━━━━━━ 💎</b>"
    return msg

def get_auth_token():
    global AUTH_TOKEN
    try:
        resp = session.post(LOGIN_URL, json={"email": GMAIL, "password": PASSWORD}, timeout=10)
        return resp.json()['data']['token']
    except: return None

# ==================== OTP SYSTEM (FIXED) ====================

def fetch_otp(chat_id, target_number):
    """এটি প্যানেলে ওটিপি চেক করবে এবং ম্যাচ করলে পাঠিয়ে দিবে"""
    token = get_auth_token()
    if not token: return
    
    target_clean = "".join(filter(str.isdigit, str(target_number)))
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        resp = session.get(f"{ORDER_URL}?date={today}&page=1", headers={"mauthtoken": token}, timeout=10).json()
        if resp and 'data' in resp and 'numbers' in resp['data']:
            for order in resp['data']['numbers']:
                order_num_clean = "".join(filter(str.isdigit, str(order.get('number', ''))))
                
                # নম্বর ম্যাচিং লজিক
                if target_clean in order_num_clean and order.get('message'):
                    full_msg = order['message']
                    otp_code = re.findall(r'\d{4,8}', full_msg)
                    code = otp_code[0] if otp_code else "N/A"
                    
                    bot.send_message(chat_id, premium_msg("✅ OTP RECEIVED", 
                        f"<b>📞 Number:</b> <code>{target_number}</code>\n"
                        f"<b>🔑 OTP Code:</b> <code>{code}</code>\n\n"
                        f"<b>💬 Message:</b>\n<code>{full_msg}</code>"))
                    return True
    except: pass
    return False

# ==================== MAIN HANDLERS ====================

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.chat.id
    USERS_DB.add(uid)
    if uid not in USER_BALANCES: USER_BALANCES[uid] = 20.0 # জয়েনিং বোনাস ২০ টাকা
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🟦 GET NUMBER 🟦", "💰 MY WALLET")
    if uid == ADMIN_ID: markup.add("⚙️ ADMIN PANEL")
    
    body = f"👋 𝗛𝗲𝗹𝗹𝗼 <b>{message.from_user.first_name}</b>!\n\n<b>Welcome to Premium Facebook Bot.</b>\n\n💵 𝗬𝗼𝘂𝗿 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: <code>{USER_BALANCES[uid]} ৳</code>"
    bot.send_message(uid, premium_msg("𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", body), reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_texts(message):
    uid = message.chat.id
    text = message.text

    if text == "🟦 GET NUMBER 🟦":
        if USER_BALANCES.get(uid, 0) < 10:
            bot.send_message(uid, "❌ <b>Insufficient Balance! Need at least 10 ৳.</b>", parse_mode="HTML")
            return
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for country, rcode in MANUAL_RANGES.items():
            markup.add(types.InlineKeyboardButton(f"📘   {country.upper()}   📘", callback_data=f"buy_{rcode}_{country}"))
        bot.send_message(uid, premium_msg("𝗦𝗘𝗟𝗘𝗖𝗧 𝗖𝗢𝗨𝗡𝗧𝗥𝗬", "<b>Choose a country for Facebook:</b>"), reply_markup=markup)

    elif text == "💰 MY WALLET":
        body = f"🆔 𝗨𝘀𝗲𝗿 𝗜𝗗: <code>{uid}</code>\n💵 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: <code>{USER_BALANCES[uid]} ৳</code>"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ ADD MONEY", callback_data="add_m"),
                   types.InlineKeyboardButton("💸 WITHDRAW", callback_data="wd"))
        bot.send_message(uid, premium_msg("𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧", body), reply_markup=markup)

    elif text == "⚙️ ADMIN PANEL" and uid == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📢 BROADCAST", callback_data="bc"),
                   types.InlineKeyboardButton("➕ ADD RANGE", callback_data="ar"),
                   types.InlineKeyboardButton("💰 ADD BALANCE TO USER", callback_data="aub"))
        bot.send_message(uid, premium_msg("𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟", f"Users: {len(USERS_DB)}"), reply_markup=markup)

# ==================== CALLBACKS ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.message.chat.id
    data = call.data

    if data.startswith("buy_"):
        prefix, country = data.split("_")[1], data.split("_")[2]
        token = get_auth_token()
        bot.edit_message_text(premium_msg("⏳ PROCESSING", "<b>Getting number from panel...</b>"), uid, call.message.message_id)
        
        try:
            res = session.post(BUY_URL, json={"range": f"{prefix}XXXX", "is_national": False, "remove_plus": False}, headers={"mauthtoken": token}).json()
            if res.get('meta', {}).get('status') == "success":
                num = res['data']['full_number']
                USER_BALANCES[uid] -= 10 # চার্জ ১০ টাকা
                
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(types.InlineKeyboardButton("📩 RECEIVE OTP 📩", callback_data=f"getotp_{num}"),
                           types.InlineKeyboardButton("🔄 CHANGE NUMBER", callback_data=f"buy_{prefix}_{country}"))
                
                bot.edit_message_text(premium_msg("✅ NUMBER READY", f"📞 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{num}</code>\n🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country}\n\n<b>Submit it on Facebook then click 'Receive OTP'</b>"), uid, call.message.message_id, reply_markup=markup)
            else: bot.answer_callback_query(call.id, "❌ No Stock!", show_alert=True)
        except: pass

    elif data.startswith("getotp_"):
        num = data.split("_")[1]
        bot.answer_callback_query(call.id, "🔎 Checking Panel for Code...")
        found = fetch_otp(uid, num)
        if not found:
            bot.answer_callback_query(call.id, "❌ No OTP yet! Try after 10 seconds.", show_alert=True)

    elif data == "ar" and uid == ADMIN_ID:
        msg = bot.send_message(uid, "<b>Send Range (Format - Name:Prefix):</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, add_range_final)

    elif data in ["add_m", "wd"]:
        bot.answer_callback_query(call.id, "Contact Admin to Process Wallet Transactions.", show_alert=True)

def add_range_final(message):
    try:
        name, pref = message.text.split(":")
        MANUAL_RANGES[name.strip()] = pref.strip()
        bot.send_message(ADMIN_ID, "✅ <b>New Range Added!</b>", parse_mode="HTML")
    except: bot.send_message(ADMIN_ID, "❌ <b>Format Error!</b>", parse_mode="HTML")

# ==================== RUN ====================
if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    print("🚀 Fixed Premium Bot is Running!")
    bot.infinity_polling(timeout=20)
