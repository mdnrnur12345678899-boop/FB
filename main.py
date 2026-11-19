import os
import threading
import time
import random
from flask import Flask
from telebot import TeleBot, types
from playwright.sync_api import sync_playwright

# --- CONFIGURATIONS ---
BOT_TOKEN = "9022049219:AAHPbUaPzMeNXz-yWNT1s8c9z4OYW3OUNng"

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

user_passwords = {}
user_manual_numbers = {}
user_states = {}

def send_telegram_message(chat_id, text, reply_markup=None):
    try:
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- REAL BROWSER AUTOMATION FLOW ---
def run_real_facebook_automation(chat_id, password, phone_number):
    send_telegram_message(chat_id, f"📱 Processing Real Browser for: `+{phone_number}`\n🚀 Launching Chromium...")

    try:
        with sync_playwright() as p:
            # হেッドレス মোডে রিয়েল ব্রাউজার রান করা
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36"
            )
            page = context.new_page()

            send_telegram_message(chat_id, "🌐 Navigating to Facebook Registration...")
            page.goto("https://m.facebook.com/reg/", timeout=60000)

            # রেন্ডম নাম সিলেক্ট
            names = [("David", "Smith"), ("James", "Johnson"), ("Mary", "Miller"), ("Patricia", "Davis"), ("John", "Williams")]
            f_name, l_name = random.choice(names)

            # ফর্ম ফিলআপ
            page.fill('input[name="firstname"]', f_name)
            page.fill('input[name="lastname"]', l_name)
            
            page.select_option('select[name="birthday_year"]', str(random.randint(1995, 2003)))
            page.select_option('select[name="birthday_month"]', str(random.randint(1, 12)))
            page.select_option('select[name="birthday_day"]', str(random.randint(1, 28)))
            
            page.fill('input[name="reg_email__"]', phone_number)
            page.fill('input[type="password"]', password)

            try:
                page.click('input[name="sex"][value="2"]') # Male
            except:
                pass

            send_telegram_message(chat_id, "🖱️ Clicking Sign Up / Next button...")
            try:
                page.click('button[type="submit"], input[type="submit"]', timeout=5000)
            except:
                pass

            # রিয়েল কুকি এবং UID খোঁজা (সর্বোচ্চ ১৫ সেকেন্ড অপেক্ষা করবে)
            send_telegram_message(chat_id, "🔍 Waiting for response and extracting real UID/Cookies...")
            uid = None
            cookie_string = ""
            
            for _ in range(15):
                time.sleep(1)
                cookies = context.cookies()
                cookie_parts = []
                for cookie in cookies:
                    cookie_parts.append(f"{cookie['name']}={cookie['value']}")
                    if cookie['name'] == 'c_user':
                        uid = cookie['value']
                if uid:
                    cookie_string = "; ".join(cookie_parts)
                    break

            browser.close()

            if uid:
                success_msg = (
                    f"🎉 **Real Account Created Successfully!**\n\n"
                    f"👤 **Real UID:** `{uid}`\n"
                    f"📱 **Phone:** `+{phone_number}`\n"
                    f"🔑 **Pass:** `{password}`\n\n"
                    f"🍪 **Real Cookie:**\n`{cookie_string}`"
                )
                send_telegram_message(chat_id, success_msg)
            else:
                send_telegram_message(chat_id, f"⚠️ Automation finished, but `c_user` cookie (UID) was not captured. Number: +{phone_number}")

    except Exception as e:
        send_telegram_message(chat_id, f"❌ Real Browser Automation Error: {str(e)}")

# --- TELEGRAM BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("🚀 FB Automation"))
    keyboard.add(types.KeyboardButton("🔑 Set Password"))
    
    welcome_text = (
        "🤖 **Render Real Browser FB Automation Bot**\n\n"
        "1. প্রথমে **'🔑 Set Password'** এ ক্লিক করে পাসওয়ার্ড দিন।\n"
        "2. এরপর **'🚀 FB Automation'** এ ক্লিক করে আপনার ম্যানুয়াল ফোন নম্বরটি পাঠান।"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "🔑 Set Password")
def ask_password(message):
    user_states[message.chat.id] = "WAITING_FOR_PASSWORD"
    bot.send_message(message.chat.id, "✍️ আপনার ফেসবুক অ্যাকাউন্টের জন্য স্থায়ী পাসওয়ার্ডটি লিখে পাঠান:")

@bot.message_handler(func=lambda msg: msg.text == "🚀 FB Automation")
def ask_phone(message):
    password = user_passwords.get(message.chat.id)
    if not password:
        bot.send_message(message.chat.id, "⚠️ দয়া করে আগে **'🔑 Set Password'** এ ক্লিক করে পাসওয়ার্ড সেট করে নিন!")
    else:
        user_states[message.chat.id] = "WAITING_FOR_PHONE"
        bot.send_message(message.chat.id, "✍️ অনুগ্রহ করে আপনার ফোন নম্বরটি লিখুন (যেমন: `237691137000`):")

@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id)

    if state == "WAITING_FOR_PASSWORD":
        user_passwords[chat_id] = text
        user_states[chat_id] = None
        bot.send_message(chat_id, f"✅ Password successfully set to: `{text}`", parse_mode="Markdown")
    
    elif state == "WAITING_FOR_PHONE":
        clean_phone = text.replace("+", "").strip()
        user_states[chat_id] = None
        password = user_passwords.get(chat_id)
        
        bot.send_message(chat_id, f"⏳ Initializing real browser for `+{clean_phone}`...")
        threading.Thread(target=run_real_facebook_automation, args=(chat_id, password, clean_phone)).start()

# --- KEEP-ALIVE FLASK SERVER FOR RENDER ---
@app.route('/')
def home():
    return "Render Playwright Bot is live and running!"

def run_flask():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # ফ্লাস্ক ব্যাকগ্রাউন্ডে রান করা (Render পোর্ট এলাইভ রাখার জন্য)
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Telegram Bot polling with Real Browser support...")
    bot.infinity_polling()
