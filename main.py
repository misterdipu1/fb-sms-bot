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
def home(): return "<b>Premium Bot is Active!</b>"

def run_web_server():
    try: app.run(host='0.0.0.0', port=8080)
    except: pass

def keep_alive():
    threading.Thread(target=run_web_server, daemon=True).start()

# ==================== CONFIGURATION ====================
# আপনার বটের টোকেন এখানে দিন
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
USERS_DB = set()

# UI DESIGN
MAIN_BTN_TEXT = "🟦   𝗚𝗘𝗧 𝗙𝗔𝗖𝗘𝗕𝗢𝗢𝗞 𝗡𝗨𝗠𝗕𝗘𝗥   🟦"
ADMIN_BTN_TEXT = "⚙️   𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟   ⚙️"

def premium_msg(title, body):
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

# ==================== OTP POLLING (FIXED) ====================

def poll_for_otp(chat_id, target_number):
    """এটি প্যানেল থেকে ওটিপি খুঁজে বের করবে"""
    start_time = time.time()
    # নম্বর থেকে শুধু ডিজিটগুলো আলাদা করা (যাতে ম্যাচিং এ ভুল না হয়)
    target_clean = re.sub(r'\D', '', str(target_number))
    
    while time.time() - start_time < 900: # ১৫ মিনিট চেক করবে
        token = get_auth_token()
        if not token: 
            time.sleep(5)
            continue
        
        headers = {"mauthtoken": token}
        # প্যানেল আজকের তারিখের অর্ডারগুলো চেক করবে
        today_date = datetime.now().strftime('%Y-%m-%d')
        url = f"{ORDER_INFO_URL}?date={today_date}&page=1"
        
        try:
            resp = session.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            if data and data.get('data') and 'numbers' in data['data']:
                orders = data['data']['numbers']
                for order in orders:
                    order_num_clean = re.sub(r'\D', '', str(order.get('number', '')))
                    
                    # যদি নম্বরটি মিলে যায় এবং মেসেজ বক্সে কিছু থাকে
                    if target_clean in order_num_clean and order.get('message'):
                        full_msg = order['message']
                        # ওটিপি কোডটি খোঁজা (৪-৮ ডিজিট)
                        otp_match = re.findall(r'\d{4,8}', full_msg)
                        otp_code = otp_match[0] if otp_match else "N/A"
                        
                        success_text = (
                            f"<b>📥 𝗡𝗘𝗪 𝗙𝗔𝗖𝗘𝗕𝗢𝗢𝗞 𝗢𝗧𝗣</b>\n\n"
                            f"<b>📞 𝗡𝘂𝗺𝗯𝗲𝗿:</b> <code>{target_number}</code>\n"
                            f"<b>🔑 𝗢𝗧𝗣 𝗖𝗼𝗱𝗲:</b> <code>{otp_code}</code>\n\n"
                            f"<b>💬 𝗙𝘂𝗹𝗹 𝗠𝗲𝘀𝘀𝗮𝗴𝗲:</b>\n<code>{full_msg}</code>"
                        )
                        bot.send_message(chat_id, premium_msg("✅ OTP RECEIVED", success_text))
                        return # ওটিপি পাওয়ার পর লুপ বন্ধ হবে
        except Exception as e:
            print(f"Polling Error: {e}")
            
        time.sleep(6) # প্রতি ৬ সেকেন্ড পর পর চেক করবে
    
    bot.send_message(chat_id, premium_msg("⏰ TIMEOUT", f"<b>OTP not received for {target_number} within 15 mins.</b>"))

# ==================== HANDLERS ====================

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.chat.id
    USERS_DB.add(uid)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton(MAIN_BTN_TEXT))
    if uid == ADMIN_ID: markup.add(types.KeyboardButton(ADMIN_BTN_TEXT))
    
    body = f"👋 𝗛𝗲𝗹𝗹𝗼 {message.from_user.first_name}!\n\n𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗙𝗮𝗰𝗲𝗯𝗼𝗼𝗸 𝗕𝗼𝘁."
    bot.send_message(uid, premium_msg("𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", body), reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.chat.id
    if message.text == MAIN_BTN_TEXT:
        bot.send_message(uid, "🔎 <b>Searching live stock...</b>", parse_mode="HTML")
        ranges = get_live_facebook_ranges()
        if not ranges:
            bot.send_message(uid, premium_msg("𝗡𝗢 𝗦𝗧𝗢𝗖𝗞", "⚠️ No live ranges found."))
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for country, rcode in ranges.items():
            markup.add(types.InlineKeyboardButton(f"📘   {country.upper()}  ({rcode[:3]})   📘", callback_data=f"buyfb_{rcode[:6]}_{country}"))
        bot.send_message(uid, premium_msg("𝗦𝗘𝗟𝗘𝗖𝗧 𝗖𝗢𝗨𝗡𝗧𝗥𝗬", "𝗖𝗵𝗼𝗼𝘀𝗲 𝗮 𝗰𝗼𝘂𝗻𝘁𝗿𝘆:"), reply_markup=markup)
    
    elif message.text == ADMIN_BTN_TEXT and uid == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📊  𝗦𝗧𝗔𝗧𝗦", callback_data="stats"))
        bot.send_message(uid, premium_msg("ADMIN PANEL", "Welcome Boss!"), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.message.chat.id
    if call.data == "stats":
        bot.send_message(uid, f"<b>Total Users: {len(USERS_DB)}</b>", parse_mode="HTML")
    
    elif call.data.startswith("buyfb_"):
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
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄   𝗖𝗛𝗔𝗡𝗚𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", callback_data=f"buyfb_{prefix}_{country}"))
                
                bot.edit_message_text(premium_msg("✅ RECEIVED", f"📞 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{num}</code>\n🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country}\n\n<b>Wait for OTP (Auto)...</b>"), uid, call.message.message_id, reply_markup=markup)
                
                # ওটিপি চেক শুরু করা (Background Thread)
                threading.Thread(target=poll_for_otp, args=(uid, num), daemon=True).start()
            else:
                bot.answer_callback_query(call.id, "❌ No Stock!", show_alert=True)
        except: pass

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
