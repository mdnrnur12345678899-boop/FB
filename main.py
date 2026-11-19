import os
import threading
import time
import random
from flask import Flask
from telebot import TeleBot, types
from playwright.sync_api import sync_playwright

BOT_TOKEN = "9022049219:AAHPbUaPzMeNXz-yWNT1s8c9z4OYW3OUNng"
FIXED_PASSWORD = "mdnur1234"

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

user_states = {}

def send_telegram_message(chat_id, text, reply_markup=None):
    try:
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- BACKGROUND REAL BROWSER AUTOMATION WITH LIVE LOGS ---
def run_facebook_automation_flow(chat_id, phone_number):
    send_telegram_message(chat_id, f"🚀 **Task Started** for phone: `+{phone_number}`")

    try:
        with sync_playwright() as p:
            send_telegram_message(chat_id, "🔧 Initializing Chromium Browser engine...")
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
                viewport={"width": 390, "height": 844},
                locale="en-US"
            )
            
            page = context.new_page()

            # স্টেপ ১: লিংক ওপেন করা
            target_url = "https://limited.facebook.com/reg/"
            send_telegram_message(chat_id, f"🌐 Opening Link: `{target_url}` ...")
            
            try:
                page.goto(target_url, timeout=60000, wait_until="domcontentloaded")
                send_telegram_message(chat_id, "✅ Link successfully opened and loaded!")
            except Exception as ex:
                send_telegram_message(chat_id, f"⚠️ `limited.facebook.com` failed, switching to `m.facebook.com/reg/`...")
                page.goto("https://m.facebook.com/reg/", timeout=60000, wait_until="domcontentloaded")
                send_telegram_message(chat_id, "✅ Backup link successfully opened!")

            time.sleep(2)

            # রেন্ডম ডাটা জেনারেট
            names = [
                ("David", "Smith"), ("James", "Johnson"), ("Mary", "Miller"), 
                ("Patricia", "Davis"), ("John", "Williams"), ("Robert", "Brown"),
                ("Michael", "Jones"), ("William", "Garcia"), ("Jennifer", "Rodriguez")
            ]
            f_name, l_name = random.choice(names)
            birth_year = str(random.randint(1995, 2003)) # 18+ বয়স নিশ্চিত করতে
            birth_month = str(random.randint(1, 12))
            birth_day = str(random.randint(1, 28))
            gender_val = random.choice(["1", "2"]) # 1=Female, 2=Male
            gender_name = "Female" if gender_val == "1" else "Male"

            # স্টেপ ২: Firstname এবং Surname বসানো
            send_telegram_message(chat_id, f"✍️ Step 1: Setting Name -> **{f_name} {l_name}**")
            page.evaluate("""(data) => {
                function setVal(element, value) {
                    const setter = Object.getOwnPropertyDescriptor(element, 'value')?.set || Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), 'value')?.set;
                    if (setter) setter.call(element, value); else element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }
                const fInput = document.querySelector('input[name="firstname"]') || document.querySelector('input[name="first_name"]');
                const lInput = document.querySelector('input[name="lastname"]') || document.querySelector('input[name="last_name"]');
                if (fInput && lInput) { setVal(fInput, data.fName); setVal(lInput, data.lName); }
            }""", {"fName": f_name, "lName": l_name})

            time.sleep(1)
            send_telegram_message(chat_id, "🖱️ Clicking 'Next' after name...")
            click_next_button(page)
            time.sleep(2)

            # স্টেপ ৩: 18+ বয়স (Birthday) বসানো
            send_telegram_message(chat_id, f"🎂 Step 2: Setting Random 18+ Age -> **{birth_day}/{birth_month}/{birth_year}**")
            page.evaluate("""(data) => {
                const yr = document.querySelector('select[name="birthday_year"]');
                const mo = document.querySelector('select[name="birthday_month"]');
                const dy = document.querySelector('select[name="birthday_day"]');
                if (yr && mo && dy) {
                    yr.value = data.birthYear; mo.value = data.birthMonth; dy.value = data.birthDay;
                    yr.dispatchEvent(new Event('change', { bubbles: true }));
                    mo.dispatchEvent(new Event('change', { bubbles: true }));
                    dy.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", {"birthYear": birth_year, "birthMonth": birth_month, "birthDay": birth_day})

            time.sleep(1)
            send_telegram_message(chat_id, "🖱️ Clicking 'Next' after age...")
            click_next_button(page)
            time.sleep(2)

            # স্টেপ ৪: ফোন নম্বর বসানো
            send_telegram_message(chat_id, f"📱 Step 3: Setting Phone Number -> **+{phone_number}**")
            page.evaluate("""(phone) => {
                const pInput = document.querySelector('input[name="reg_email__"]') || document.querySelector('input[type="tel"]');
                if (pInput) {
                    const setter = Object.getOwnPropertyDescriptor(pInput, 'value')?.set || Object.getOwnPropertyDescriptor(Object.getPrototypeOf(pInput), 'value')?.set;
                    if (setter) setter.call(pInput, phone); else pInput.value = phone;
                    pInput.dispatchEvent(new Event('input', { bubbles: true }));
                    pInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", phone_number)

            time.sleep(1)
            send_telegram_message(chat_id, "🖱️ Clicking 'Next' after phone number...")
            click_next_button(page)
            time.sleep(2)

            # স্টেপ ৫: জেন্ডার সিলেক্ট করা
            send_telegram_message(chat_id, f"⚥ Step 4: Selecting Gender -> **{gender_name}**")
            page.evaluate("""(gender) => {
                const gRadio = document.querySelector(`input[name="sex"][value="${gender}"]`);
                if (gRadio) { 
                    gRadio.click(); 
                    gRadio.checked = true; 
                    gRadio.dispatchEvent(new Event('change', { bubbles: true })); 
                }
            }""", gender_val)

            time.sleep(1)
            send_telegram_message(chat_id, "🖱️ Clicking 'Next' after gender...")
            click_next_button(page)
            time.sleep(2)

            # স্টেপ ৬: পাসওয়ার্ড (mdnur1234) বসানো
            send_telegram_message(chat_id, f"🔑 Step 5: Setting Fixed Password -> **{FIXED_PASSWORD}**")
            page.evaluate("""(password) => {
                const pwdInput = document.querySelector('input[type="password"]') || document.querySelector('input[name="reg_passwd__"]');
                if (pwdInput) {
                    const setter = Object.getOwnPropertyDescriptor(pwdInput, 'value')?.set || Object.getOwnPropertyDescriptor(Object.getPrototypeOf(pwdInput), 'value')?.set;
                    if (setter) setter.call(pwdInput, password); else pwdInput.value = password;
                    pwdInput.dispatchEvent(new Event('input', { bubbles: true }));
                    pwdInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", FIXED_PASSWORD)

            time.sleep(1)
            
            # স্টেপ ৭: ফাইনাল সাইন আপ ক্লিক
            send_telegram_message(chat_id, "🖱️ Step 6: Clicking final 'Sign Up' button...")
            click_signup_button(page)

            # স্টেপ ৮: ৮-১০ সেকেন্ড প্রসেসিং ও কুকি ক্যাপচার
            send_telegram_message(chat_id, "⏳ Processing (8-10 seconds) & capturing real UID/Cookies...")
            
            uid = None
            cookie_string = ""
            
            for i in range(12):
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

            # ফাইনাল আউটপুট
            if uid:
                success_msg = (
                    f"🎉 **Account Created Successfully!**\n\n"
                    f"👤 **UID:** `{uid}`\n"
                    f"📱 **Phone:** `+{phone_number}`\n"
                    f"🔑 **Password:** `{FIXED_PASSWORD}`\n\n"
                    f"🍪 **Full Cookie:**\n`{cookie_string}`"
                )
                send_telegram_message(chat_id, success_msg)
            else:
                send_telegram_message(chat_id, f"⚠️ Automation finished for `+{phone_number}`, but `c_user` cookie was not caught. (The number might require OTP code or already taken).")

    except Exception as e:
        send_telegram_message(chat_id, f"❌ Automation Critical Error: {str(e)}")

def click_next_button(page):
    try:
        page.evaluate("""() => {
            const buttons = document.querySelectorAll('button, input[type="submit"], div[role="button"]');
            for (let b of buttons) {
                const t = (b.innerText || b.value || b.getAttribute('aria-label') || '').toLowerCase();
                if (t.includes('next') || t.includes('পরবর্তী') || t.includes('continue') || t.includes('लगاتار')) {
                    b.click();
                    break;
                }
            }
        }""")
    except:
        pass

def click_signup_button(page):
    try:
        page.evaluate("""() => {
            const buttons = document.querySelectorAll('button, input[type="submit"], div[role="button"]');
            for (let b of buttons) {
                const t = (b.innerText || b.value || b.getAttribute('aria-label') || '').toLowerCase();
                if (t.includes('sign up') || t.includes('signup') || t.includes('সাইন আপ') || t.includes('register') || t.includes('finish')) {
                    b.click();
                    break;
                }
            }
        }""")
    except:
        pass

# --- TELEGRAM BOT INTERFACE ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("🚀 Create Account"))
    
    welcome_text = (
        "🤖 **FB Live Log Account Creator Bot**\n\n"
        "• পাসওয়ার্ড ফিক্সড: `mdnur1234`\n"
        "• প্রতিটি স্টেপের লাইভ আপডেট দেখতে পাবেন।\n\n"
        "নিচের **'🚀 Create Account'** বাটনে ক্লিক করুন:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "🚀 Create Account")
def ask_phone(message):
    user_states[message.chat.id] = "WAITING_FOR_PHONE"
    bot.send_message(message.chat.id, "✍️ আপনার ফোন নম্বরটি এখানে লিখে পাঠান (যেমন: `237691137000`):")

@bot.message_handler(func=lambda msg: msg.text and not msg.text.startswith('/'))
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id)

    if state == "WAITING_FOR_PHONE":
        clean_phone = text.replace("+", "").strip()
        user_states[chat_id] = None
        
        bot.send_message(chat_id, f"⏳ Task queued for `+{clean_phone}`...")
        threading.Thread(target=run_facebook_flow, args=(chat_id, clean_phone)).start()

@app.route('/')
def home():
    return "FB Live Log Bot is active!"

def run_flask():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        bot.remove_webhook()
    except:
        pass
    print("Bot with Live Logs started...")
    bot.infinity_polling(skip_pending=True)
