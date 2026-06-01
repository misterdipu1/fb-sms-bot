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
def home(): return "<b>Premium SMS Bot is Online!</b>"
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

# ইন-মেমোরি ডাটাবেজ (সার্ভার রিস্টার্ট দিলে রিসেট হবে)
USER_BALANCES = {} # {user_id: balance}
MANUAL_RANGES = {"Ivory Coast 🇨🇮": "22507", "Bangladesh 🇧🇩": "88017", "India 🇮🇳": "919"}
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

def get_panel_balance():
    token = get_auth_token()
    try:
        resp = session.get(INFO_URL, headers={"mauthtoken": token}, timeout=10)
        return resp.json()['data']['balance']
    except: return "0.00"

# ==================== MAIN HANDLERS ====================

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.chat.id
    USERS_DB.add(uid)
    if uid not in USER_BALANCES: USER_BALANCES[uid] = 50.0 # নতুন ইউজারকে ৫০ টাকা গিফট
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📲 GET NUMBER", "💰 MY WALLET")
    if uid == ADMIN_ID: markup.add("⚙️ ADMIN PANEL")
    
    body = f"👋 𝗛𝗲𝗹𝗹𝗼 <b>{message.from_user.first_name}</b>!\n\n<b>Welcome to Premium Facebook SMS Service.</b>\n\n💵 𝗬𝗼𝘂𝗿 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: <code>{USER_BALANCES[uid]} ৳</code>"
    bot.send_message(uid, premium_msg("𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", body), reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_texts(message):
    uid = message.chat.id
    text = message.text

    if text == "📲 GET NUMBER":
        if USER_BALANCES.get(uid, 0) < 10:
            bot.send_message(uid, "❌ <b>Insufficient Balance! Please Add Money.</b>", parse_mode="HTML")
            return
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for country, rcode in MANUAL_RANGES.items():
            markup.add(types.InlineKeyboardButton(f"📘   {country.upper()}   📘", callback_data=f"buy_{rcode}_{country}"))
        bot.send_message(uid, premium_msg("𝗦𝗘𝗟𝗘𝗖𝗧 𝗖𝗢𝗨𝗡𝗧𝗥𝗬", "<b>Choose a country to get Facebook Number:</b>"), reply_markup=markup)

    elif text == "💰 MY WALLET":
        body = f"🆔 𝗨𝘀𝗲𝗿 𝗜𝗗: <code>{uid}</code>\n💵 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: <code>{USER_BALANCES[uid]} ৳</code>\n\n💳 <b>To Add Balance or Withdraw, Contact Admin.</b>"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ ADD MONEY", callback_data="add_money"),
                   types.InlineKeyboardButton("💸 WITHDRAW", callback_data="withdraw"))
        bot.send_message(uid, premium_msg("𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧", body), reply_markup=markup)

    elif text == "⚙️ ADMIN PANEL" and uid == ADMIN_ID:
        p_bal = get_panel_balance()
        body = f"🏢 𝗣𝗮𝗻𝗲𝗹 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: <code>{p_bal} $</code>\n👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: <code>{len(USERS_DB)}</code>"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📢 BROADCAST", callback_data="bc"),
                   types.InlineKeyboardButton("➕ ADD RANGE", callback_data="add_range"),
                   types.InlineKeyboardButton("💰 ADD USER BALANCE", callback_data="add_ubal"))
        bot.send_message(uid, premium_msg("𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟", body), reply_markup=markup)

# ==================== CALLBACKS (BUY, OTP, ADMIN) ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.message.chat.id
    data = call.data

    if data.startswith("buy_"):
        prefix, country = data.split("_")[1], data.split("_")[2]
        token = get_auth_token()
        bot.edit_message_text(premium_msg("⏳ PROCESSING", "Fetching your number..."), uid, call.message.message_id)
        
        try:
            res = session.post(BUY_URL, json={"range": f"{prefix}XXXX", "is_national": False, "remove_plus": False}, headers={"mauthtoken": token}).json()
            if res.get('meta', {}).get('status') == "success":
                num = res['data']['full_number']
                USER_BALANCES[uid] -= 10 # প্রতি নম্বরে ১০ টাকা চার্জ
                
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(types.InlineKeyboardButton("📩 RECEIVE OTP", callback_data=f"otp_{num}"),
                           types.InlineKeyboardButton("🔄 CHANGE NUMBER", callback_data=f"buy_{prefix}_{country}"))
                
                bot.edit_message_text(premium_msg("✅ NUMBER READY", f"📞 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{num}</code>\n🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country}\n\n<b>Submit on Facebook & Click 'Receive OTP'</b>"), uid, call.message.message_id, reply_markup=markup)
            else: bot.answer_callback_query(call.id, "❌ No Stock!", show_alert=True)
        except: pass

    elif data.startswith("otp_"):
        target_num = data.split("_")[1]
        token = get_auth_token()
        bot.answer_callback_query(call.id, "🔎 Checking for OTP...")
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            orders = session.get(f"{ORDER_URL}?date={today}&page=1", headers={"mauthtoken": token}).json()['data']['numbers']
            for o in orders:
                if "".join(filter(str.isdigit, str(target_num))) in "".join(filter(str.isdigit, str(o['number']))):
                    if o.get('message'):
                        otp = re.findall(r'\d{4,8}', o['message'])[0]
                        bot.send_message(uid, premium_msg("📥 OTP RECEIVED", f"📞 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{target_num}</code>\n🔑 𝗢𝗧𝗣 𝗖𝗼𝗱𝗲: <code>{otp}</code>\n\n💬 𝗠𝘀𝗴: <code>{o['message']}</code>"))
                        return
            bot.answer_callback_query(call.id, "❌ No OTP yet! Try again in 10s.", show_alert=True)
        except: pass

    elif data == "add_range" and uid == ADMIN_ID:
        msg = bot.send_message(uid, "<b>Enter Country Name and Prefix (e.g. Russia:7999):</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, save_range)

    elif data == "withdraw" or data == "add_money":
        bot.answer_callback_query(call.id, "Contact @YourAdminUsername to process.", show_alert=True)

def save_range(message):
    try:
        name, pref = message.text.split(":")
        MANUAL_RANGES[name.strip()] = pref.strip()
        bot.send_message(ADMIN_ID, "✅ <b>Range Added Successfully!</b>", parse_mode="HTML")
    except: bot.send_message(ADMIN_ID, "❌ <b>Format Error! Use Name:Prefix</b>", parse_mode="HTML")

# ==================== START ====================
if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    print("🚀 Premium All-in-One Bot Started!")
    bot.infinity_polling(timeout=20)
