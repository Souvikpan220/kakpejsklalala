cat > bot.py << 'ENDOFBOT'
import telebot
from telebot import types
import json
import time
import threading
import config
import database as db
from admin_panel import AdminPanel
from utils.decorators import check_limit, check_banned, maintenance_check

bot = telebot.TeleBot(config.BOT_TOKEN)
admin_panel = AdminPanel(bot)
user_states = {}
db.init_database()

print("🌟 BRONX OSINT BOT STARTED!")
print("👑 Admin Panel Active!")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    first_name = message.from_user.first_name or "User"
    db.register_user(user_id, username, first_name)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("📱 NUMBER INFO", callback_data="menu_number_info"),
        types.InlineKeyboardButton("🆔 AADHAR INFO", callback_data="menu_aadhar_info"),
        types.InlineKeyboardButton("🚗 VEHICLE INFO", callback_data="menu_vehicle_info"),
        types.InlineKeyboardButton("🏦 IFSC INFO", callback_data="menu_ifsc_info"),
        types.InlineKeyboardButton("📞 TG TO NUMBER", callback_data="menu_telegram_info"),
        types.InlineKeyboardButton("🎮 FREE FIRE", callback_data="menu_freefire_info"),
        types.InlineKeyboardButton("📮 PINCODE", callback_data="menu_pincode_info"),
        types.InlineKeyboardButton("📱 IMEI INFO", callback_data="menu_imei_info"),
        types.InlineKeyboardButton("🌐 IP INFO", callback_data="menu_ip_info"),
        types.InlineKeyboardButton("📸 INSTAGRAM", callback_data="menu_instagram_info"),
        types.InlineKeyboardButton("🪪 AADHAR RATION", callback_data="menu_aadhar_ration"),
        types.InlineKeyboardButton("💳 BUY PREMIUM", callback_data="show_plans"),
    ]
    markup.add(*buttons)
    
    bot.send_message(message.chat.id, f"🌟 *WELCOME TO BRONX OSINT BOT*\n\n👤 User: {first_name}\n🆔 ID: `{user_id}`\n🔍 Remaining: {db.get_remaining_searches(user_id)}\n\n🔰 Select a feature:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def menu_handler(call):
    user_id = call.from_user.id
    if db.is_banned(user_id):
        bot.answer_callback_query(call.id, "❌ You are banned!", show_alert=True)
        return
    
    user_states[user_id] = call.data
    
    examples = {
        'menu_number_info': '📱 Send 10 Digit Number\nExample: `9876543210`',
        'menu_aadhar_info': '🆔 Send 12 Digit Aadhar\nExample: `393933081942`',
        'menu_vehicle_info': '🚗 Send Vehicle Number\nExample: `MH02FZ0555`',
        'menu_ifsc_info': '🏦 Send IFSC Code\nExample: `SBIN0001234`',
        'menu_telegram_info': '📞 Send Telegram ID\nExample: `7530266953`',
        'menu_freefire_info': '🎮 Send FF UID\nExample: `123456789`',
        'menu_pincode_info': '📮 Send 6 Digit Pincode\nExample: `110001`',
        'menu_imei_info': '📱 Send 15 Digit IMEI\nExample: `357817383506298`',
        'menu_ip_info': '🌐 Send IP Address\nExample: `8.8.8.8`',
        'menu_instagram_info': '📸 Send Username\nExample: `cristiano`',
        'menu_aadhar_ration': '🪪 Send Mobile Number\nExample: `701984830542`',
    }
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu"))
    
    bot.edit_message_text(call.message.chat.id, call.message.message_id, f"🔰 *Feature Selected*\n\n{examples.get(call.data, 'Send query')}\n\n⚠️ Remaining: {db.get_remaining_searches(user_id)}", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
def back_to_menu(call):
    if call.from_user.id in user_states:
        del user_states[call.from_user.id]
    send_welcome(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'show_plans')
def show_plans(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    plans = [
        ("💎 5 Days - ₹50 (50)", "plan_5days"),
        ("💎 10 Days - ₹100 (100)", "plan_10days"),
        ("💎 20 Days - ₹200 (200)", "plan_20days"),
        ("💎 30 Days - ₹300 (Unlimited)", "plan_30days"),
        ("💎 60 Days - ₹600 (Unlimited)", "plan_60days"),
        ("💎 100 Days - ₹999 (Unlimited)", "plan_100days"),
        ("👑 Lifetime - ₹3000", "plan_lifetime"),
        ("📞 Contact Owner", "contact_owner"),
        ("🔙 Back", "back_to_menu"),
    ]
    for t, c in plans:
        markup.add(types.InlineKeyboardButton(t, callback_data=c))
    bot.edit_message_text(call.message.chat.id, call.message.message_id, "💳 *PREMIUM PLANS*\n\nChoose your plan:\n\n📞 @BRONX_ULTRA", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('plan_') or call.data == 'contact_owner')
def plan_detail(call):
    if call.data == 'contact_owner':
        bot.answer_callback_query(call.id, "Contact @BRONX_ULTRA on Telegram!", show_alert=True)
        return
    plans = {
        'plan_5days': ('5 Days', '₹50', '50'),
        'plan_10days': ('10 Days', '₹100', '100'),
        'plan_20days': ('20 Days', '₹200', '200'),
        'plan_30days': ('30 Days', '₹300', 'Unlimited'),
        'plan_60days': ('60 Days', '₹600', 'Unlimited'),
        'plan_100days': ('100 Days', '₹999', 'Unlimited'),
        'plan_lifetime': ('Lifetime', '₹3000', 'Unlimited'),
    }
    p = plans.get(call.data, ('Unknown', 'N/A', 'N/A'))
    bot.answer_callback_query(call.id, f"{p[0]}: {p[1]} - {p[2]} searches\nContact @BRONX_ULTRA", show_alert=True)

@bot.message_handler(func=lambda m: True)
@maintenance_check
@check_banned
def handle_all(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text.startswith('/admin') and (str(user_id) == str(config.ADMIN_ID) or db.is_admin(user_id)):
        admin_panel.process_command(message)
        return
    
    if user_id in user_states:
        feature = user_states[user_id]
        if not db.decrement_search(user_id) and not db.is_vip(user_id):
            handle_limit_exceeded(message)
            return
        
        handler_map = {
            'menu_number_info': 'number_info', 'menu_aadhar_info': 'aadhar_info',
            'menu_vehicle_info': 'vehicle_info', 'menu_ifsc_info': 'ifsc_info',
            'menu_telegram_info': 'telegram_info', 'menu_freefire_info': 'freefire_info',
            'menu_pincode_info': 'pincode_info', 'menu_imei_info': 'imei_info',
            'menu_ip_info': 'ip_info', 'menu_instagram_info': 'instagram_info',
            'menu_aadhar_ration': 'aadhar_ration'
        }
        
        handler_name = handler_map.get(feature)
        if handler_name:
            try:
                import importlib
                handler = importlib.import_module(f'handlers.{handler_name}')
                db.log_search(user_id, handler_name, text)
                handler.process(bot, message)
                del user_states[user_id]
            except Exception as e:
                bot.reply_to(message, f"❌ Error: {e}")
    else:
        bot.reply_to(message, "🏠 Use /start to begin", parse_mode="Markdown")

def handle_limit_exceeded(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 VIEW PLANS", callback_data="show_plans"))
    markup.add(types.InlineKeyboardButton("📞 CONTACT", url="https://t.me/BRONX_ULTRA"))
    bot.send_message(message.chat.id, "❌ *LIMIT EXCEEDED!*\n\nYour search limit is over!\nUpgrade to continue.\n\n📞 @BRONX_ULTRA", parse_mode="Markdown", reply_markup=markup)

if __name__ == "__main__":
    t = threading.Thread(target=admin_panel.start_monitoring, daemon=True)
    t.start()
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
ENDOFBOT
