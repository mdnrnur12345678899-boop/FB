import os
import threading
import time
import random
import subprocess
import json
from flask import Flask
from telebot import TeleBot, types

BOT_TOKEN = "9022049219:AAHPbUaPzMeNXz-yWNT1s8c9z4OYW3OUNng"
FIXED_PASSWORD = "mdnur1234"

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)
user_states = {}

def send_telegram_message(chat_id, text):
    try:
        bot.send_message(chat_id, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- WORKER SCRIPT TO RUN PLAYWRIGHT SAFELY IN SEPARATE PROCESS ---
# এটি ব্যাকগ্রাউন্ডে আলাদা প্রসেস হিসেবে চলবে, ফলে বট কখনোই জ্যাম বা ফ্রিজ হবে না।
WORKER_CODE = """
import sys
import time
import random
from playwright.sync_api import sync_playwright

phone_number = sys.argv[1]
password = sys.argv[2]

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
            viewport={"width": 390, "height": 844},
            locale="en-US"
        )
        page = context.new_page()

        try:
            page.goto("https://limited.facebook.com/reg/", timeout=40000, wait_until="domcontentloaded")
        except:
            page.goto("https://m.facebook.com/reg/", timeout=40000, wait_until="domcontentloaded")

        time.sleep(2)

        names = [("David", "Smith"), ("James", "Johnson"), ("Mary", "Miller"), ("Patricia", "Davis"), ("John", "Williams"), ("Robert", "Brown")]
        f_name, l_name = random.choice(names)
        birth_year = str(random.randint(1995, 2003))
        birth_month = str(random.randint(1, 12))
        birth_day = str(random.randint(1, 28))
        gender_val = random.choice(["1", "2"])

        page.evaluate(\"\"\"(data) => {
            function setVal(element, value) {
                const setter = Object.getOwnPropertyDescriptor(element, 'value')?.set || Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), 'value')?.set;
                if (setter) setter.call(element, value); else element.value = value;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }
            const fInput = document.querySelector('input[name="firstname"]') || document.querySelector('input[name="first_name"]');
            const lInput = document.querySelector('input[name="lastname"]') || document.querySelector('input[name="last_name"]');
            if (fInput && lInput) { setVal(fInput, data.fName); setVal(lInput, data.lName); }
        } \"\"\", {"fName": f_name, "lName": l_name})

        time.sleep(1)
        click_next(page)
        time.sleep(2)

        page.evaluate(\"\"\"(data) => {
            const yr = document.querySelector('select[name="birthday_year"]');
            const mo = document.querySelector('select[name="birthday_month"]');
            const dy = document.querySelector('select[name="birthday_day"]');
            if (yr && mo && dy) {
                yr.value = data.birthYear; mo.value = data.birthMonth; dy.value = data.birthDay;
                yr.dispatchEvent(new Event('change', { bubbles: true }));
                mo.dispatchEvent(new Event('change', { bubbles: true }));
                dy.dispatchEvent(new Event('change', { bubbles: true }));
            }
        } \"\"\", {"birthYear": birth_year, "birthMonth": birth_month, "birthDay": birth_day})

        time.sleep(1)
        click_next(page)
        time.sleep(2)

        page.evaluate(\"\"\"(phone) => {
            const pInput = document.querySelector('input[name="reg_email__"]') || document.querySelector('input[type="tel"]');
            if (pInput) {
                const setter = Object.getOwnPropertyDescriptor(pInput, 'value')?.set || Object.getOwnPropertyDescriptor(Object.getPrototypeOf(pInput), 'value')?.set;
                if (setter) setter.call(pInput, phone); else pInput.value = phone;
                pInput.dispatchEvent(new Event('input', { bubbles: true }));
                pInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        } \"\"\", phone_number)

        time.sleep(1)
        click_next(page)
        time.sleep(2)

        page.evaluate(\"\"\"(gender) => {
            const gRadio = document.querySelector(`input[name="sex"][value="${gender}"]`);
            if (gRadio) { gRadio.click(); gRadio.checked = true; gRadio.dispatchEvent(new Event('change', { bubbles: true })); }
        } \"\"\", gender_val)

        time.sleep(1)
        click_next(page)
        time.sleep(2)

        page.evaluate(\"\"\"(password) => {
            const pwdInput = document.querySelector('input[type="password"]') || document.querySelector('input[name="reg_passwd__"]');
            if (pwdInput) {
                const setter = Object.getOwnPropertyDescriptor(pwdInput, 'value')?.set || Object.getOwnPropertyDescriptor(Object.getPrototypeOf(pwdInput), 'value')?.set;
                if (setter) setter.call(pwdInput, password); else pwdInput.value = password;
                pwdInput.dispatchEvent(new Event('input', { bubbles: true }));
                pwdInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        } \"\"\", password)

        time.sleep(1)
        click_signup(page)

        uid = None
        cookie_string = ""
        for _ in range(12):
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
        
        # JSON ফরম্যাটে রেজাল্ট প্রিন্ট করা যাতে বট এটি রিড করতে পারে
        print("RESULT_JSON_START")
        print(json.dumps({"success": True, "uid": uid, "cookies": cookie_string}))
        print("RESULT_JSON_END")

    except Exception as e:
        print("RESULT_JSON_START")
        print(json.dumps({"success": False, "error": str(e)}))
        print("RESULT_JSON_END")

def click_next(page):
    try:
        page.evaluate(\"\"\"() => {
            const buttons = document.querySelectorAll('button, input[type="submit"], div[role="button"]');
            for (let b of buttons) {
                const t = (b.innerText || b.value || b.getAttribute('aria-label') || '').toLowerCase();
                if (t.includes('next') || t.includes('পরবর্তী') || t.includes('continue')) { b.click(); break; }
            }
        } \"\"\")
    except: pass

def click_signup(page):
    try:
        page.evaluate(\"\"\"() => {
            const buttons = document.querySelectorAll('button, input[type="submit"], div[role="button"]');
            for (let b of buttons) {
                const t = (b.innerText || b.value || b.getAttribute('aria-label') || '').toLowerCase();
                if (t.includes('sign up') || t.includes('signup') || t.includes('সাইন আপ') || t.includes('register')) { b.click(); break; }
            }
        } \"\"\")
    except: pass
"""

# worker.py ফাইল তৈরি করে রাখা
with open("worker.py", "w") as f:
    f.write(WORKER_CODE)


def run_automation_in_background(chat_id, phone_number):
    send_telegram_message(chat_id, f"⏳ Browser process started for `+{phone_number}`. Please wait 10-15 seconds...")
    
    try:
        # আলাদা সাবপ্রসেসে worker.py রান করা
        process = subprocess.Popen(
            ["python", "worker.py", phone_number, FIXED_PASSWORD],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(timeout=45) # সর্বোচ্চ ৪৫ সেকেন্ড টাইমআউট
        
        # আউটপুট থেকে JSON রেজাল্ট খুঁজে বের করা
        if "RESULT_JSON_START" in stdout:
            json_str = stdout.split("RESULT_JSON_START")[1].split("RESULT_JSON_END")[0].strip()
            res = json.loads(json_str)
            
            if res.get("success"):
                uid = res.get("uid")
                cookies = res.get("cookies")
                if uid:
                    success_msg = (
                        f"🎉 **Account Created Successfully!**\n\n"
                        f"👤 **UID:** `{uid}`\n"
                        f"📱 **Phone:** `+{phone_number}`\n"
                        f"🔑 **Password:** `{FIXED_PASSWORD}`\n\n"
                        f"🍪 **Full Cookie:**\n`{cookies}`"
                    )
                    send_telegram_message(chat_id, success_msg)
                else:
                    send_telegram_message(chat_id, f"⚠️ Automation finished for `+{phone_number}`, but `c_user` cookie was not captured. (Number might need verification).")
            else:
                err = res.get("error", "Unknown error")
                send_telegram_message(chat_id, f"❌ Automation Worker Error: `{err}`")
        else:
            send_telegram_message(chat_id, f"❌ Process finished without valid output. Log: {stdout[-200:]}")

    except subprocess.TimeoutExpired:
        send_telegram_message(chat_id, f"❌ Process timed out (45s exceeded) for `+{phone_number}`.")
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Execution Exception: {str(e)}")


# --- TELEGRAM BOT ROUTING ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("🚀 Create Account"))
    
    welcome_text = (
        "🤖 **FB Subprocess Automation Bot**\n\n"
        "• পাসওয়ার্ড ফিক্সড: `mdnur1234`\n"
        "• এখন আর বট জ্যাম বা ফ্রিজ হবে না।\n\n"
        "নিচের **'🚀 Create Account'** বাটনে ক্লিক করুন:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "🚀 Create Account")
def ask_phone(message):
    user_states[message.chat.id] = "WAITING_FOR_PHONE"
    send_telegram_message(message.chat.id, "✍️ আপনার ফোন নম্বরটি এখানে লিখে পাঠান (যেমন: `237691137000`):")

@bot.message_handler(func=lambda msg: msg.text and not msg.text.startswith('/'))
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id)

    if state == "WAITING_FOR_PHONE":
        clean_phone = text.replace("+", "").strip()
        user_states[chat_id] = None
        
        send_telegram_message(chat_id, f"⏳ Task accepted for `+{clean_phone}`. Launching subprocess...")
        threading.Thread(target=run_automation_in_background, args=(chat_id, clean_phone)).start()

@app.route('/')
def home():
    return "FB Subprocess Bot is active!"

def run_flask():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        bot.remove_webhook()
    except:
        pass
    print("Bot with Subprocess Handler started...")
    bot.infinity_polling(skip_pending=True)
