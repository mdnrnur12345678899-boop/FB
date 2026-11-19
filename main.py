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

# --- BACKROUND REAL BROWSER AUTOMATION STEP-BY-STEP ---
def run_facebook_automation_flow(chat_id, phone_number):
    send_telegram_message(chat_id, f"🚀 Starting FB Automation for phone: `+{phone_number}`\n⏳ Please wait 8-10 seconds...")

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
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
                viewport={"width": 390, "height": 844},
                locale="en-US"
            )
            
            page = context.new_page()

            # স্টেপ ১: নির্দিষ্ট লিংকে যাওয়া
            send_telegram_message(chat_id, "🌐 Opening limited.facebook.com/reg/ ...")
            try:
                page.goto("https://limited.facebook.com/reg/", timeout=60000, wait_until="domcontentloaded")
            except:
                page.goto("https://m.facebook.com/reg/", timeout=60000, wait_until="domcontentloaded")

            time.sleep(2)

            # রেন্ডম নাম এবং বয়স জেনারেট করা (18+ অর্থাৎ ১৯৯৫ থেকে ২০০৩ এর মধ্যে)
            names = [
                ("David", "Smith"), ("James", "Johnson"), ("Mary", "Miller"), 
                ("Patricia", "Davis"), ("John", "Williams"), ("Robert", "Brown"),
                ("Michael", "Jones"), ("William", "Garcia"), ("Jennifer", "Rodriguez")
            ]
            f_name, l_name = random.choice(names)
            birth_year = str(random.randint(1995, 2003))
            birth_month = str(random.randint(1, 12))
            birth_day = str(random.randint(1, 28))
            gender_val = random.choice(["1", "2"]) # 1=Female, 2=Male

            # স্টেপ ২ থেকে ৮ পর্যন্ত ব্রাউজারে অটো ফিল এবং ক্লিক করার মূল স্ক্রিপ্ট
            send_telegram_message(chat_id, "✍️ Auto-filling Name, Age, Phone, Gender & Password...")
            
            page.evaluate("""(data) => {
                function setVal(element, value) {
                    const setter = Object.getOwnPropertyDescriptor(element, 'value')?.set || Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), 'value')?.set;
                    if (setter) setter.call(element, value); else element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }

                // ১. Firstname এবং Surname বসানো
                const fInput = document.querySelector('input[name="firstname"]') || document.querySelector('input[name="first_name"]');
                const lInput = document.querySelector('input[name="lastname"]') || document.querySelector('input[name="last_name"]');
                if (fInput && lInput) { setVal(fInput, data.fName); setVal(lInput, data.lName); }
            }""", {"fName": f_name, "lName": l_name})

            time.sleep(1)
            
            # প্রথম নেক্সট ক্লিক (Name এর পর)
            click_next_button(page)
            time.sleep(2)

            # ২. 18+ রেন্ডম বয়স (Birthday) বসানো এবং নেক্সট ক্লিক
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
            click_next_button(page)
            time.sleep(2)

            # ৩. ফোন নাম্বার বসানো এবং নেক্সট ক্লিক
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
            click_next_button(page)
            time.sleep(2)

            # ৪. জেন্ডার সিলেক্ট করা এবং নেক্সট ক্লিক
            page.evaluate("""(gender) => {
                const gRadio = document.querySelector(`input[name="sex"][value="${gender}"]`);
                if (gRadio) { 
                    gRadio.click(); 
                    gRadio.checked = true; 
                    gRadio.dispatchEvent(new Event('change', { bubbles: true })); 
                }
            }""", gender_val)

            time.sleep(1)
            click_next_button(page)
            time.sleep(2)

            # ৫. পাসওয়ার্ড (mdnur1234) বসানো এবং সাইন আপ / ফাইনাল ক্লিক
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
            
            # ফাইনাল সাইন আপ / রেজিস্টার বাটনে ক্লিক
            send_telegram_message(chat_id, "🖱️ Clicking final Sign Up button...")
            click_signup_button(page)

            # স্টেপ ৯: ৮-১০ সেকেন্ড প্রসেসিং হওয়া এবং কুকি থেকে UID বের করা
            send_telegram_message(chat_id, "⏳ Processing (8-10 seconds) & capturing UID/Cookies...")
            
            uid = None
            cookie_string = ""
            
            for _ in range(12): # প্রায় ১২ সেকেন্ড ট্র্যাকিং চলবে
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

            # ফলাফল টেলিগ্রাম বটে পাঠানো
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
                send_telegram_message(chat_id, f"⚠️ Automation completed for `+{phone_number}`, but `c_user` cookie was not caught. (The number might require OTP verification or already registered).")

    except Exception as e:
        send_telegram_message(chat_id, f"❌ Automation Process Error: {str(e)}")

# সহায়ক ক্লিক ফাংশনসমূহ
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

# --- TELEGRAM BOT ROUTING ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("🚀 Create Account"))
    
    welcome_text = (
        "🤖 **FB Auto Account Creator Bot**\n\n"
        "• পাসওয়ার্ড ফিক্সড করা আছে: `mdnur1234`\n"
        "• নাম, বয়স, জেন্ডার অটোমেটিক রেন্ডম নিয়ে নিবে।\n\n"
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
        
        bot.send_message(chat_id, f"⏳ Task accepted for `+{clean_phone}`. Starting background process...")
        threading.Thread(target=run_facebook_flow, args=(chat_id, clean_phone)).start()

@app.route('/')
def home():
    return "FB Auto Creator Bot is active!"

def run_flask():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        bot.remove_webhook()
    except:
        pass
    print("Bot started successfully...")
    bot.infinity_polling(skip_pending=True)
