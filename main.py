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

# ইন-মেমোরি ডাটাবেজ (সার্ভার রিস্টার্ট দিলে এটি রিসেট হবে)
USER_BALANCES = {} # {user_id: balance}
MANUAL_RANGES = {"Ivory Coast 🇨🇮": "22507", "Bangladesh 🇧🇩": "88017", "India 🇮🇳": "919"}
USERS_DB = set()
CURRENT_NUMBERS = {} # {user_id: current_number}

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
    if uid not in USER_BALANCES: USER_BALANCES[uid] = 100.0 # নতুন ইউজারকে ১০০ টাকা গিফট
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("🟦  𝗚𝗘𝗧 𝗡𝗨𝗠𝗕𝗘𝗥  🟦"), types.KeyboardButton("👤  𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧  👤"))
    if uid == ADMIN_ID:
        markup.add(types.KeyboardButton("⚙️  𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟  ⚙️"))
    
    body = f"👋 𝗛𝗲𝗹𝗹𝗼 <b>{message.from_user.first_name}</b>!\n\n<b>Welcome to our High-Speed SMS Service.</b>\n\n💵 𝗬𝗼𝘂𝗿 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: <code>{USER_BALANCES[uid]} ৳</code>"
    bot.send_message(uid, premium_msg("𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", body), reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_texts(message):
    uid = message.chat.id
    text = message.text

    if "𝗚𝗘𝗧 𝗡𝗨𝗠𝗕𝗘𝗥" in text:
        if USER_BALANCES.get(uid, 0) < 10:
            bot.send_message(uid, "<b>❌ Insufficient Balance! Please add money to your wallet.</b>", parse_mode="HTML")
            return
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for country, rcode in MANUAL_RANGES.items():
            markup.add(types.InlineKeyboardButton(f"📘   {country.upper()}   📘", callback_data=f"buy_{rcode}_{country}"))
        bot.send_message(uid, premium_msg("𝗦𝗘𝗟𝗘𝗖𝗧 𝗖𝗢𝗨𝗡𝗧𝗥𝗬", "<b>Choose a country to get Facebook Number:</b>"), reply_markup=markup)

    elif "𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧" in text:
        body = f"🆔 𝗨𝘀𝗲𝗿 𝗜𝗗: <code>{uid}</code>\n💵 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: <code>{USER_BALANCES[uid]} ৳</code>\n\n💳 <b>To add money or withdraw, contact our support team.</b>"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕  𝗔𝗗𝗗 𝗠𝗢𝗡𝗘𝗬", callback_data="contact_admin"),
                   types.InlineKeyboardButton("💸  𝗪𝗜𝗧𝗛𝗗𝗥𝗔𝗪", callback_data="contact_admin"))
        bot.send_message(uid, premium_msg("𝗠𝗬 𝗪𝗔𝗟𝗟𝗘𝗧", body), reply_markup=markup)

    elif "𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟" in text and uid == ADMIN_ID:
        p_bal = get_panel_balance()
        body = f"🏢 𝗣𝗮𝗻𝗲ｌ 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: <code>{p_bal} $</code>\n👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: <code>{len(USERS_DB)}</code>"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📢  𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧  📢", callback_data="broadcast"),
                   types.InlineKeyboardButton("➕  𝗔𝗗𝗗 𝗥𝗔𝗡𝗚𝗘", callback_data="add_range"),
                   types.InlineKeyboardButton("💰  𝗔𝗗𝗗 𝗕𝗔𝗟𝗔𝗡𝗖𝗘", callback_data="add_ubal"))
        bot.send_message(uid, premium_msg("𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟", body), reply_markup=markup)

# ==================== CALLBACKS ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.message.chat.id
    data = call.data

    if data.startswith("buy_"):
        prefix, country = data.split("_")[1], data.split("_")[2]
        token = get_auth_token()
        bot.edit_message_text(premium_msg("⏳ 𝗣𝗥𝗢𝗖𝗘𝗦𝗦𝗜𝗡𝗚", "<b>Fetching a fresh number for you...</b>"), uid, call.message.message_id)
        
        try:
            res = session.post(BUY_URL, json={"range": f"{prefix}XXXX", "is_national": False, "remove_plus": False}, headers={"mauthtoken": token}).json()
            if res.get('meta', {}).get('status') == "success":
                num = res['data']['full_number']
                USER_BALANCES[uid] -= 10.0 # নম্বর প্রতি ১০ টাকা কাটবে
                CURRENT_NUMBERS[uid] = num # ওটিপি চেক করার জন্য সেভ রাখা
                
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(types.InlineKeyboardButton("📩  𝗥𝗘𝗖𝗘𝗜𝗩𝗘 𝗢𝗧𝗣  📩", callback_data=f"getotp_{num}"),
                           types.InlineKeyboardButton("🔄  𝗖𝗛𝗔𝗡𝗚𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", callback_data=f"buy_{prefix}_{country}"))
                
                bot.edit_message_text(premium_msg("✅ 𝗡𝗨𝗠𝗕𝗘𝗥 𝗥𝗘𝗔𝗗𝗬", f"📞 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{num}</code>\n🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country}\n\n<b>Submit this number on Facebook and then click 'Receive OTP'.</b>"), uid, call.message.message_id, reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "❌ No Stock for this range!", show_alert=True)
                bot.edit_message_text(premium_msg("𝗡𝗢 𝗦𝗧𝗢𝗖𝗞", "<b>Try another country.</b>"), uid, call.message.message_id)
        except: pass

    elif data.startswith("getotp_"):
        target_num = data.split("_")[1]
        token = get_auth_token()
        bot.answer_callback_query(call.id, "🔎 Checking for OTP...")
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            resp = session.get(f"{ORDER_URL}?date={today}&page=1", headers={"mauthtoken": token}).json()
            orders = resp['data']['numbers']
            
            clean_target = "".join(filter(str.isdigit, str(target_num)))
            for o in orders:
                clean_order_num = "".join(filter(str.isdigit, str(o['number'])))
                if clean_target in clean_order_num and o.get('message'):
                    msg_body = o['message']
                    otp_code = re.findall(r'\d{4,8}', msg_body)[0]
                    bot.send_message(uid, premium_msg("📥 𝗢𝗧𝗣 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗", f"📞 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{target_num}</code>\n🔑 𝗢𝗧𝗣 𝗖𝗼𝗱𝗲: <code>{otp_code}</code>\n\n💬 𝗠𝘀𝗴: <code>{msg_body}</code>"))
                    return
            bot.answer_callback_query(call.id, "❌ No OTP yet! Send code again or wait.", show_alert=True)
        except:
            bot.answer_callback_query(call.id, "❌ Error fetching OTP.")

    elif data == "contact_admin":
        bot.answer_callback_query(call.id, "Contact @YourAdminUsername to proceed.", show_alert=True)

    elif data == "add_range":
        msg = bot.send_message(uid, "<b>Enter Name & Prefix (e.g. Russia:799):</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, save_manual_range)

def save_manual_range(message):
    try:
        name, pref = message.text.split(":")
        MANUAL_RANGES[name.strip()] = pref.strip()
        bot.send_message(ADMIN_ID, "✅ <b>Range Added!</b>")
    except: bot.send_message(ADMIN_ID, "❌ <b>Wrong Format!</b>")

# ==================== RUN BOT ====================
if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    print("🚀 Premium All-in-One Bot is Live!")
    bot.infinity_polling(timeout=20)
