import telebot
from telebot import types
import time
import threading
import importlib
import config
import database as db
from admin_panel import AdminPanel

bot = telebot.TeleBot(config.BOT_TOKEN)
admin = AdminPanel(bot)
user_state = {}

db.init_database()

print("""
╔══════════════════════════════════╗
║   🌟 BRONX OSINT BOT V1.0 🌟   ║
║   👑 Owner: @BRONX_ULTRA       ║
║   ✅ Bot Started Successfully   ║
╚══════════════════════════════════╝
""")

# ============ START COMMAND ============
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    uname = message.from_user.username or ""
    fname = message.from_user.first_name or "User"
    
    db.register_user(uid, uname, fname)
    rem = db.get_remaining_searches(uid)
    banned = db.is_banned(uid)
    
    if banned:
        bot.send_message(message.chat.id, "🚫 *YOU ARE BANNED!*\n\nContact @BRONX_ULTRA", parse_mode="Markdown")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        [types.InlineKeyboardButton("📱 NUMBER INFO", callback_data="m_number")],
        [types.InlineKeyboardButton("🆔 AADHAR INFO", callback_data="m_aadhar")],
        [types.InlineKeyboardButton("🚗 VEHICLE INFO", callback_data="m_vehicle")],
        [types.InlineKeyboardButton("🏦 IFSC INFO", callback_data="m_ifsc")],
        [types.InlineKeyboardButton("📞 TG TO NUMBER", callback_data="m_telegram")],
        [types.InlineKeyboardButton("🎮 FREE FIRE", callback_data="m_ff")],
        [types.InlineKeyboardButton("📮 PINCODE", callback_data="m_pincode")],
        [types.InlineKeyboardButton("📱 IMEI INFO", callback_data="m_imei")],
        [types.InlineKeyboardButton("🌐 IP INFO", callback_data="m_ip")],
        [types.InlineKeyboardButton("📸 INSTAGRAM", callback_data="m_insta")],
        [types.InlineKeyboardButton("🪪 AADHAR RATION", callback_data="m_ration")],
        [types.InlineKeyboardButton("💳 BUY PREMIUM", callback_data="show_plans")],
        [types.InlineKeyboardButton("ℹ️ HELP", callback_data="show_help")],
    ]
    
    for row in buttons:
        markup.add(*row)
    
    welcome = f"""
🌟 *WELCOME TO BRONX OSINT BOT* 🌟

┏━━━━━━━━━━━━━━━━━━━━┓
👤 *User:* {fname}
🆔 *ID:* `{uid}`
📊 *Status:* 🟢 Active
🔍 *Remaining:* {rem}
┗━━━━━━━━━━━━━━━━━━━━┛

🔰 *Select a feature below:*
    """
    
    bot.send_message(message.chat.id, welcome, parse_mode="Markdown", reply_markup=markup)

# ============ MENU CALLBACKS ============
@bot.callback_query_handler(func=lambda c: c.data.startswith('m_'))
def menu_callback(call):
    uid = call.from_user.id
    
    if db.is_banned(uid):
        bot.answer_callback_query(call.id, "❌ Banned!", show_alert=True)
        return
    
    user_state[uid] = call.data
    
    feature_map = {
        'm_number': '📱 NUMBER INFO',
        'm_aadhar': '🆔 AADHAR INFO',
        'm_vehicle': '🚗 VEHICLE INFO',
        'm_ifsc': '🏦 IFSC INFO',
        'm_telegram': '📞 TELEGRAM TO NUMBER',
        'm_ff': '🎮 FREE FIRE INFO',
        'm_pincode': '📮 PINCODE INFO',
        'm_imei': '📱 IMEI INFO',
        'm_ip': '🌐 IP INFO',
        'm_insta': '📸 INSTAGRAM INFO',
        'm_ration': '🪪 AADHAR RATION INFO',
    }
    
    examples = {
        'm_number': '📝 Send 10 Digit Number\nExample: `9876543210`',
        'm_aadhar': '📝 Send 12 Digit Aadhar\nExample: `393933081942`',
        'm_vehicle': '📝 Send Vehicle Number\nExample: `MH02FZ0555`',
        'm_ifsc': '📝 Send IFSC Code\nExample: `SBIN0001234`',
        'm_telegram': '📝 Send Telegram User ID\nExample: `7530266953`',
        'm_ff': '📝 Send Free Fire UID\nExample: `123456789`',
        'm_pincode': '📝 Send 6 Digit Pincode\nExample: `110001`',
        'm_imei': '📝 Send 15 Digit IMEI\nExample: `357817383506298`',
        'm_ip': '📝 Send IP Address\nExample: `8.8.8.8`',
        'm_insta': '📝 Send Instagram Username\nExample: `cristiano`',
        'm_ration': '📝 Send Mobile Number\nExample: `701984830542`',
    }
    
    fname = feature_map.get(call.data, "Feature")
    ex = examples.get(call.data, "Send your query")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back_menu"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"""
🔰 *{fname}*

┏━━━━━━━━━━━━━━━━━━━━┓
{ex}
┗━━━━━━━━━━━━━━━━━━━━┛

⚠️ *Remaining:* {db.get_remaining_searches(uid)}
        """,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ============ BACK TO MENU ============
@bot.callback_query_handler(func=lambda c: c.data == 'back_menu')
def back_menu(call):
    if call.from_user.id in user_state:
        del user_state[call.from_user.id]
    start_cmd(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)

# ============ HELP ============
@bot.callback_query_handler(func=lambda c: c.data == 'show_help')
def show_help(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 BACK", callback_data="back_menu"))
    
    help_text = """
📚 *HELP MENU*

┏━━━━━━━━━━━━━━━━━━━━┓
🔰 *Features:*
• 📱 Number Info
• 🆔 Aadhar Info
• 🚗 Vehicle Info
• 🏦 IFSC Info
• 📞 Telegram to Number
• 🎮 Free Fire Info
• 📮 Pincode Info
• 📱 IMEI Info
• 🌐 IP Info
• 📸 Instagram Info
• 🪪 Aadhar Ration Info

💳 *Premium Plans Available*
👑 *Owner:* @BRONX_ULTRA
┗━━━━━━━━━━━━━━━━━━━━┛
    """
    bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

# ============ PREMIUM PLANS ============
@bot.callback_query_handler(func=lambda c: c.data == 'show_plans')
def show_plans(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    plans = [
        ("💎 5 Days - ₹50 (50 Searches)", "plan_5"),
        ("💎 10 Days - ₹100 (100 Searches)", "plan_10"),
        ("💎 20 Days - ₹200 (200 Searches)", "plan_20"),
        ("💎 30 Days - ₹300 (Unlimited)", "plan_30"),
        ("💎 60 Days - ₹600 (Unlimited)", "plan_60"),
        ("💎 100 Days - ₹999 (Unlimited 24/7)", "plan_100"),
        ("👑 LIFETIME - ₹3000 (Unlimited)", "plan_life"),
        ("📞 CONTACT OWNER", "contact_owner"),
        ("🔙 BACK", "back_menu"),
    ]
    
    for text, cb in plans:
        if cb == "contact_owner":
            markup.add(types.InlineKeyboardButton(text, url="https://t.me/BRONX_ULTRA"))
        else:
            markup.add(types.InlineKeyboardButton(text, callback_data=cb))
    
    plan_text = """
💳 *PREMIUM PLANS*

┏━━━━━━━━━━━━━━━━━━━━┓
💎 5 Days - ₹50
   ↳ 50 Searches

💎 10 Days - ₹100
   ↳ 100 Searches

💎 20 Days - ₹200
   ↳ 200 Searches

💎 30 Days - ₹300
   ↳ Unlimited Searches

💎 60 Days - ₹600
   ↳ Unlimited Searches

💎 100 Days - ₹999
   ↳ Unlimited 24/7

👑 Lifetime - ₹3000
   ↳ No Limit, Unlimited
┗━━━━━━━━━━━━━━━━━━━━┛

📞 *Contact @BRONX_ULTRA to buy*
    """
    bot.edit_message_text(plan_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

# ============ PLAN DETAILS ============
@bot.callback_query_handler(func=lambda c: c.data.startswith('plan_'))
def plan_details(call):
    plans_info = {
        'plan_5': ('5 Days', '₹50', '50 Searches'),
        'plan_10': ('10 Days', '₹100', '100 Searches'),
        'plan_20': ('20 Days', '₹200', '200 Searches'),
        'plan_30': ('30 Days', '₹300', 'Unlimited'),
        'plan_60': ('60 Days', '₹600', 'Unlimited'),
        'plan_100': ('100 Days', '₹999', 'Unlimited 24/7'),
        'plan_life': ('Lifetime', '₹3000', 'Unlimited'),
    }
    
    info = plans_info.get(call.data, ('Unknown', 'N/A', 'N/A'))
    
    detail = f"""
📋 *PLAN DETAILS*

┏━━━━━━━━━━━━━━━━━━━━┓
📌 *Plan:* {info[0]}
💰 *Price:* {info[1]}
🔍 *Searches:* {info[2]}

✨ *Benefits:*
✅ Full Access All Features
✅ Priority Support
✅ Fast Results
✅ 24/7 Availability
┗━━━━━━━━━━━━━━━━━━━━┛

📞 Contact @BRONX_ULTRA
    """
    bot.answer_callback_query(call.id, f"{info[0]}: {info[1]} - {info[2]}\nContact @BRONX_ULTRA", show_alert=True)

# ============ HANDLE MESSAGES ============
@bot.message_handler(func=lambda m: True)
def handle_all_msg(message):
    uid = message.from_user.id
    txt = message.text.strip()
    
    # Admin commands
    if txt.startswith('/admin') and (str(uid) == str(config.ADMIN_ID) or db.is_admin(uid)):
        admin.process(message)
        return
    
    # Check banned
    if db.is_banned(uid):
        bot.reply_to(message, "🚫 *BANNED!*\nContact @BRONX_ULTRA", parse_mode="Markdown")
        return
    
    # Check maintenance
    if db.is_maintenance():
        bot.reply_to(message, "🔧 *MAINTENANCE MODE*\nTry later.", parse_mode="Markdown")
        return
    
    # Feature processing
    if uid in user_state:
        feature = user_state[uid]
        
        # Check limit
        if not db.is_vip(uid):
            if not db.decrement_search(uid):
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("💳 VIEW PLANS", callback_data="show_plans"),
                    types.InlineKeyboardButton("📞 CONTACT", url="https://t.me/BRONX_ULTRA")
                )
                
                limit_msg = """
❌ *LIMIT EXCEEDED!*

┏━━━━━━━━━━━━━━━━━━━━┓
😔 Your search limit is over!

💎 *Available Plans:*
• 5 Days - ₹50 (50 Searches)
• 10 Days - ₹100 (100 Searches)
• 20 Days - ₹200 (200 Searches)
• 30 Days - ₹300 (Unlimited)
• 60 Days - ₹600 (Unlimited)
• 100 Days - ₹999 (Unlimited)
• Lifetime - ₹3000 (Unlimited)

📞 *Contact:* @BRONX_ULTRA
┗━━━━━━━━━━━━━━━━━━━━┛
                """
                bot.send_message(message.chat.id, limit_msg, parse_mode="Markdown", reply_markup=markup)
                return
        
        # Handler mapping
        handler_map = {
            'm_number': 'number_info',
            'm_aadhar': 'aadhar_info',
            'm_vehicle': 'vehicle_info',
            'm_ifsc': 'ifsc_info',
            'm_telegram': 'telegram_info',
            'm_ff': 'freefire_info',
            'm_pincode': 'pincode_info',
            'm_imei': 'imei_info',
            'm_ip': 'ip_info',
            'm_insta': 'instagram_info',
            'm_ration': 'aadhar_ration',
        }
        
        handler_name = handler_map.get(feature)
        
        if handler_name:
            try:
                handler = importlib.import_module(f'handlers.{handler_name}')
                db.log_search(uid, handler_name, txt)
                handler.process(bot, message)
                del user_state[uid]
            except Exception as e:
                bot.reply_to(message, f"❌ Error: {e}")
        else:
            bot.reply_to(message, "❌ Invalid feature")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🌟 START BOT", callback_data="back_menu"))
        bot.reply_to(message, "🏠 Use /start to begin", reply_markup=markup)

# ============ RUN BOT ============
if __name__ == "__main__":
    t = threading.Thread(target=admin.start_monitor, daemon=True)
    t.start()
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Polling Error: {e}")
            time.sleep(5)

# Isko bot.py ke LAST mein add karo (if __name__ == "__main__": ke upar)
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    import threading
    threading.Thread(target=admin.start_monitor, daemon=True).start()
    threading.Thread(target=run_flask, daemon=True).start()
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
