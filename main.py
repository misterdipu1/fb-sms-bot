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
def home(): return "<b>Premium Facebook Bot is Online!</b>"

def run_web_server():
    try: app.run(host='0.0.0.0', port=8080)
    except: pass

def keep_alive():
    threading.Thread(target=run_web_server, daemon=True).start()

# ==================== CONFIGURATION ====================
# --- এখানে আপনার নতুন টোকেনটি বসান ---
BOT_TOKEN = "8959798750:AAGrFOXgKQhl19_ZbWBqFHGwsMFc_bG3omU" 

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

# ইন-মেমোরি ডাটাবেজ (সার্ভার রিস্টার্ট দিলে এটি ক্লিয়ার হবে)
USERS_DB = set()

# ==================== UI DESIGN & STYLING ====================
MAIN_BTN_TEXT = "🟦   𝗚𝗘𝗧 𝗙𝗔𝗖𝗘𝗕𝗢𝗢𝗞 𝗡𝗨𝗠𝗕𝗘𝗥   🟦"
ADMIN_BTN_TEXT = "⚙️   𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟   ⚙️"

def premium_msg(title, body):
    """সব মেসেজ বোল্ড এবং প্রিমিয়াম লুক দিবে"""
    msg = f"<b>💎 ━━━━━━━━━━━━━━ 💎</b>\n"
    msg += f"<b>👑 {title} 👑</b>\n"
    msg += f"<b>━━━━━━━━━━━━━━</b>\n\n"
    msg += f"<b>{body}</b>\n\n"
    msg += f"<b>💎 ━━━━━━━━━━━━━━ 💎</b>"
    return msg

# ==================== CORE API FUNCTIONS ====================

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

def poll_for_otp(chat_id, target_number, msg_id):
    """ব্যাকগ্রাউন্ডে ওটিপি চেক করার লজিক"""
    start_time = time.time()
    while time.time() - start_time < 600: # ১০ মিনিট চেক করবে
        token = get_auth_token()
        if not token: continue
        
        headers = {"mauthtoken": token}
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"{ORDER_INFO_URL}?date={today}&page=1"
        try:
            resp = session.get(url, headers=headers, timeout=10)
            data = resp.json()
            if data and 'data' in data:
                numbers = data['data'].get('numbers', [])
                for entry in numbers:
                    if str(entry.get('number')) == str(target_number) and entry.get('message'):
                        full_msg = entry['message']
                        otp = re.findall(r'\d{4,8}', full_msg)
                        otp_code = otp[0] if otp else "N/A"
                        
                        bot.send_message(chat_id, premium_msg("📥 NEW FACEBOOK OTP", 
                            f"<b>📞 Number:</b> <code>{target_number}</code>\n"
                            f"<b>🔑 OTP Code:</b> <code>{otp_code}</code>\n\n"
                            f"<b>💬 Full Message:</b>\n<code>{full_msg}</code>"))
                        return
        except: pass
        time.sleep(5)
    bot.send_message(chat_id, "<b>⏰ Timeout: Facebook OTP not received within 10 minutes.</b>")

# ==================== ADMIN PANEL HANDLERS ====================

@bot.callback_query_handler(func=lambda call: call.data in ["stats", "broadcast", "admin_main"])
def admin_callbacks(call):
    uid = call.message.chat.id
    if uid != ADMIN_ID: return

    if call.data == "admin_main":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📊  𝗧𝗢𝗧𝗔𝗟 𝗨𝗦𝗘𝗥𝗦", callback_data="stats"),
            types.InlineKeyboardButton("📢  𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘", callback_data="broadcast")
        )
        bot.edit_message_text(premium_msg("ADMIN PANEL", "<b>Welcome Boss! Choose an option:</b>"), uid, call.message.message_id, reply_markup=markup)

    elif call.data == "stats":
        bot.answer_callback_query(call.id)
        bot.send_message(uid, premium_msg("STATISTICS", f"<b>Total Registered Users: {len(USERS_DB)}</b>"))

    elif call.data == "broadcast":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(uid, "<b>✏️ Enter your message to broadcast to all users:</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    count = 0
    for user in USERS_DB:
        try:
            bot.send_message(user, premium_msg("📢 ANNOUNCEMENT", message.text))
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"<b>✅ Broadcast complete. Sent to {count} users.</b>", parse_mode="HTML")

# ==================== USER HANDLERS ====================

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.chat.id
    USERS_DB.add(uid) # ইউজার সেভ করা
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton(MAIN_BTN_TEXT))
    if uid == ADMIN_ID:
        markup.add(types.KeyboardButton(ADMIN_BTN_TEXT))
    
    welcome_body = (
        f"<b>👋 𝗛𝗲𝗹𝗹𝗼 {message.from_user.first_name}!</b>\n\n"
        "<b>𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗼𝘂𝗿 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗙𝗮𝗰𝗲𝗯𝗼𝗼𝗸 𝗦𝗠𝗦 𝗦𝗲𝗿𝘃𝗶𝗰𝗲.</b>\n"
        "<b>𝗚𝗲𝘁 𝗵𝗶𝗴𝗵-𝗾𝘂𝗮𝗹𝗶𝘁𝘆 𝗻𝘂𝗺𝗯𝗲𝗿𝘀 𝗶𝗻𝘀𝘁𝗮𝗻𝘁𝗹𝘆.</b>"
    )
    bot.send_message(uid, premium_msg("𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", welcome_body), reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.chat.id
    text = message.text

    if text == MAIN_BTN_TEXT:
        bot.send_message(uid, "<b>🔎 𝗦𝗲𝗮𝗿𝗰𝗵𝗶𝗻𝗴 𝗟𝗶𝘃𝗲 𝗦𝘁𝗼𝗰𝗸...</b>", parse_mode="HTML")
        ranges = get_live_facebook_ranges()
        if not ranges:
            bot.send_message(uid, premium_msg("𝗡𝗢 𝗦𝗧𝗢Ｃ𝗞", "<b>⚠️ No live Facebook ranges found right now.</b>"))
            return

        markup = types.InlineKeyboardMarkup(row_width=1)
        for country, rcode in ranges.items():
            btn_label = f"📘   {country.upper()}  ({rcode[:3]})   📘"
            markup.add(types.InlineKeyboardButton(btn_label, callback_data=f"buyfb_{rcode[:6]}_{country}"))
        bot.send_message(uid, premium_msg("𝗦𝗘𝗟𝗘𝗖𝗧 𝗖𝗢𝗨𝗡𝗧𝗥𝗬", "<b>𝗖𝗵𝗼𝗼𝘀𝗲 𝗮 𝗹𝗶𝘃𝗲 𝗰𝗼𝘂𝗻𝘁𝗿𝘆:</b>"), reply_markup=markup)

    elif text == ADMIN_BTN_TEXT and uid == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📊  𝗧𝗢𝗧𝗔𝗟 𝗨𝗦𝗘𝗥𝗦", callback_data="stats"),
            types.InlineKeyboardButton("📢  𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘", callback_data="broadcast")
        )
        bot.send_message(uid, premium_msg("ADMIN PANEL", "<b>Admin Access Granted.</b>"), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buyfb_"))
def handle_buy(call):
    uid = call.message.chat.id
    token = get_auth_token()
    parts = call.data.split("_")
    prefix, country = parts[1], parts[2]
    
    bot.edit_message_text(premium_msg("⏳ 𝗣𝗥𝗢𝗖𝗘𝗦𝗦𝗜𝗡𝗚", f"<b>𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗶𝗻𝗴 {country} 𝗻𝘂𝗺𝗯𝗲𝗿...</b>"), uid, call.message.message_id)
    
    headers = {"mauthtoken": token, "Content-Type": "application/json"}
    payload = {"range": f"{prefix}XXXX", "is_national": False, "remove_plus": False}
    
    try:
        resp = session.post(BUY_NUMBER_URL, json=payload, headers=headers, timeout=10)
        res = resp.json()
        if res.get('meta', {}).get('status') == "success":
            num = res['data']['full_number']
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🔄   𝗖𝗛𝗔𝗡𝗚𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", callback_data=f"buyfb_{prefix}_{country}"))
            
            bot.edit_message_text(premium_msg("✅ RECEIVED", f"<b>📞 Number:</b> <code>{num}</code>\n<b>🌍 Country: {country}</b>\n\n<b>Wait for OTP...</b>"), uid, call.message.message_id, reply_markup=markup)
            
            # ওটিপি চেক শুরু করা (Background Thread)
            threading.Thread(target=poll_for_otp, args=(uid, num, call.message.message_id), daemon=True).start()
        else:
            bot.answer_callback_query(call.id, "❌ No Stock!", show_alert=True)
    except:
        bot.answer_callback_query(call.id, "❌ API Error!")

# ==================== START BOT ====================
if __name__ == "__main__":
    keep_alive()
    print("🚀 Cleaning old sessions...")
    bot.remove_webhook()
    time.sleep(1)
    print("🚀 Premium Facebook Bot is Starting...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
