import os
import threading
import time
import random
from flask import Flask
from telebot import TeleBot, types
from playwright.sync_api import sync_playwright

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

def run_real_facebook_automation(chat_id, password, phone_number):
    send_telegram_message(chat_id, f"⚡ Starting Limited FB Automation for: `+{phone_number}`")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            
            # মোবাইল ইউজার এজেন্ট সেট করা (আপনার অ্যান্ড্রয়েড অ্যাপের মতো)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
                viewport={"width": 390, "height": 844},
                locale="en-US"
            )
            
            page = context.new_page()

            send_telegram_message(chat_id, "🌐 Opening limited.facebook.com/reg/ ...")
            
            # আপনি যেটা চাচ্ছেন: সরাসরি limited.facebook.com অথবা m.facebook.com/reg/ এ যাওয়া
            try:
                page.goto("https://limited.facebook.com/reg/", timeout=60000, wait_until="domcontentloaded")
            except:
                page.goto("https://m.facebook.com/reg/", timeout=60000, wait_until="domcontentloaded")

            time.sleep(3)
            send_telegram_message(chat_id, "✍️ Auto-filling name, bday, phone & password...")

            # রেন্ডম নাম
            names = [("David", "Smith"), ("James", "Johnson"), ("Mary", "Miller"), ("Patricia", "Davis"), ("John", "Williams"), ("Robert", "Brown")]
            f_name, l_name = random.choice(names)

            birth_year = str(random.randint(1995, 2003))
            birth_month = str(random.randint(1, 12))
            birth_day = str(random.randint(1, 28))

            # আপনার অ্যান্ড্রয়েড অ্যাপের লজিকের আদলে জাভাস্ক্রিপ্ট ইভালুয়েট করে ফর্মে ডাটা বসানো (সবচেয়ে ফাস্ট ও কার্যকরী পদ্ধতি)
            page.evaluate("""(data) => {
                function setVal(element, value) {
                    const setter = Object.getOwnPropertyDescriptor(element, 'value')?.set || Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), 'value')?.set;
                    if (setter) setter.call(element, value); else element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }

                // নাম
                const fInput = document.querySelector('input[name="firstname"]') || document.querySelector('input[name="first_name"]');
                const lInput = document.querySelector('input[name="lastname"]') || document.querySelector('input[name="last_name"]');
                if (fInput && lInput) { setVal(fInput, data.fName); setVal(lInput, data.lName); }

                // জন্মতারিখ
                const yr = document.querySelector('select[name="birthday_year"]');
                const mo = document.querySelector('select[name="birthday_month"]');
                const dy = document.querySelector('select[name="birthday_day"]');
                if (yr && mo && dy) {
                    yr.value = data.birthYear; mo.value = data.birthMonth; dy.value = data.birthDay;
                    yr.dispatchEvent(new Event('change', { bubbles: true }));
                    mo.dispatchEvent(new Event('change', { bubbles: true }));
                    dy.dispatchEvent(new Event('change', { bubbles: true }));
                }

                // ফোন নম্বর
                const pInput = document.querySelector('input[name="reg_email__"]') || document.querySelector('input[type="tel"]');
                if (pInput) { setVal(pInput, data.phone); }

                // জেন্ডার (Male = 2)
                const gRadio = document.querySelector('input[name="sex"][value="2"]');
                if (gRadio) { gRadio.click(); gRadio.checked = true; gRadio.dispatchEvent(new Event('change', { bubbles: true })); }

                // পাসওয়ার্ড
                const pwdInput = document.querySelector('input[type="password"]') || document.querySelector('input[name="reg_passwd__"]');
                if (pwdInput) { setVal(pwdInput, data.password); }
            }""", {
                "fName": f_name,
                "lName": l_name,
                "birthYear": birth_year,
                "birthMonth": birth_month,
                "birthDay": birth_day,
                "phone": phone_number,
                "password": password
            })

            time.sleep(2)
            send_telegram_message(chat_id, "🖱️ Clicking Next / Sign Up button automatically...")

            # নেক্সট বা সাইন আপ বাটনে ক্লিক করা
            page.evaluate("""() => {
                const buttons = document.querySelectorAll('button, input[type="submit"], div[role="button"]');
                for (let b of buttons) {
                    const t = (b.innerText || b.value || b.getAttribute('aria-label') || '').toLowerCase();
                    if (t.includes('next') || t.includes('sign up') || t.includes('পরবর্তী') || t.includes('continue') || t.includes('সাইন আপ')) {
                        b.click();
                        break;
                    }
                }
            """)

            send_telegram_message(chat_id, "🔍 Waiting for registration completion & capturing cookies...")
            
            uid = None
            cookie_string = ""
            
            # সর্বোচ্চ ২০ সেকেন্ড সময় নিয়ে কুকি ও UID ট্র্যাক করা
            for _ in range(20):
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
                    f"🎉 **Limited FB Account Created Successfully!**\n\n"
                    f"👤 **Real UID:** `{uid}`\n"
                    f"📱 **Phone:** `+{phone_number}`\n"
                    f"🔑 **Pass:** `{password}`\n\n"
                    f"🍪 **Real Cookie:**\n`{cookie_string}`"
                )
                send_telegram_message(chat_id, success_msg)
            else:
                send_telegram_message(chat_id, f"⚠️ Automation executed on limited.facebook.com, but `c_user` cookie was not caught instantly. Number: +{phone_number}. (Check if OTP verification page appeared).")

    except Exception as e:
        send_telegram_message(chat_id, f"❌ Automation Error: {str(e)}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("🚀 FB Automation"))
    keyboard.add(types.KeyboardButton("🔑 Set Password"))
    
    welcome_text = (
        "🤖 **Limited FB Automation Bot**\n\n"
        "1. প্রথমে **'🔑 Set Password'** এ ক্লিক করে পাসওয়ার্ড দিন।\n"
        "2. এরপর **'🚀 FB Automation'** এ ক্লিক করে আপনার ফোন নম্বরটি পাঠান।"
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

@bot.message_handler(func=lambda msg: msg.text and not msg.text.startswith('/'))
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
        
        bot.send_message(chat_id, f"⏳ Running automation on limited.facebook.com for `+{clean_phone}`...")
        threading.Thread(target=run_real_facebook_automation, args=(chat_id, password, clean_phone)).start()

@app.route('/')
def home():
    return "Limited FB Automation Bot is live!"

def run_flask():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
