import telebot
from telebot import types
import time, threading
import config, database as db
from admin_panel import AdminPanel
from utils.decorators import check_limit, check_banned, maintenance_check

bot = telebot.TeleBot(config.BOT_TOKEN)
admin_panel = AdminPanel(bot)
user_states = {}
db.init_database()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    uid = message.from_user.id
    uname = message.from_user.username or "User"
    fname = message.from_user.first_name or "User"
    db.register_user(uid, uname, fname)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
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
        types.InlineKeyboardButton("💳 PREMIUM", callback_data="show_plans"),
    ]
    markup.add(*btns)
    bot.send_message(message.chat.id, f"🌟 *BRONX OSINT BOT*\n\n👤 {fname}\n🆔 `{uid}`\n🔍 {db.get_remaining_searches(uid)}", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith('menu_'))
def menu_handler(call):
    uid = call.from_user.id
    if db.is_banned(uid):
        bot.answer_callback_query(call.id, "Banned!", show_alert=True)
        return
    user_states[uid] = call.data
    ex = {
        'menu_number_info': 'Send 10 Digit Number\nExample: 9876543210',
        'menu_aadhar_info': 'Send 12 Digit Aadhar\nExample: 393933081942',
        'menu_vehicle_info': 'Send Vehicle No\nExample: MH02FZ0555',
        'menu_ifsc_info': 'Send IFSC Code\nExample: SBIN0001234',
        'menu_telegram_info': 'Send Telegram ID\nExample: 7530266953',
        'menu_freefire_info': 'Send FF UID\nExample: 123456789',
        'menu_pincode_info': 'Send 6 Digit Pincode\nExample: 110001',
        'menu_imei_info': 'Send 15 Digit IMEI\nExample: 357817383506298',
        'menu_ip_info': 'Send IP Address\nExample: 8.8.8.8',
        'menu_instagram_info': 'Send Username\nExample: cristiano',
        'menu_aadhar_ration': 'Send Mobile Number\nExample: 701984830542',
    }
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu"))
    bot.edit_message_text(f"🔰 *Feature*\n\n{ex.get(call.data)}\n\n⚠️ {db.get_remaining_searches(uid)}", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == 'back_to_menu')
def back(call):
    if call.from_user.id in user_states: del user_states[call.from_user.id]
    send_welcome(call.message)

@bot.callback_query_handler(func=lambda c: c.data == 'show_plans')
def plans(call):
    mk = types.InlineKeyboardMarkup(row_width=1)
    for t, cb in [("5 Days - ₹50", "p_5"),("10 Days - ₹100", "p_10"),("30 Days - ₹300", "p_30"),("Lifetime - ₹3000", "p_life"),("📞 @BRONX_ULTRA", "p_contact"),("🔙 Back", "back_to_menu")]:
        mk.add(types.InlineKeyboardButton(t, callback_data=cb))
    bot.edit_message_text("💳 *PLANS*\n\nContact @BRONX_ULTRA", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=mk)

@bot.message_handler(func=lambda m: True)
@maintenance_check
@check_banned
def handle_all(message):
    uid = message.from_user.id
    txt = message.text.strip()
    if txt.startswith('/admin') and (str(uid)==str(config.ADMIN_ID) or db.is_admin(uid)):
        admin_panel.process_command(message)
        return
    if uid in user_states:
        f = user_states[uid]
        if not db.decrement_search(uid) and not db.is_vip(uid):
            mk = types.InlineKeyboardMarkup()
            mk.add(types.InlineKeyboardButton("💳 PLANS", callback_data="show_plans"))
            bot.send_message(message.chat.id, "❌ *LIMIT EXCEEDED!*\n\n📞 @BRONX_ULTRA", parse_mode="Markdown", reply_markup=mk)
            return
        hm = {'menu_number_info':'number_info','menu_aadhar_info':'aadhar_info','menu_vehicle_info':'vehicle_info','menu_ifsc_info':'ifsc_info','menu_telegram_info':'telegram_info','menu_freefire_info':'freefire_info','menu_pincode_info':'pincode_info','menu_imei_info':'imei_info','menu_ip_info':'ip_info','menu_instagram_info':'instagram_info','menu_aadhar_ration':'aadhar_ration'}
        h = hm.get(f)
        if h:
            import importlib
            handler = importlib.import_module(f'handlers.{h}')
            db.log_search(uid, h, txt)
            handler.process(bot, message)
            del user_states[uid]
    else:
        bot.reply_to(message, "🏠 Use /start")

if __name__ == "__main__":
    threading.Thread(target=admin_panel.start_monitoring, daemon=True).start()
    while True:
        try: bot.polling(none_stop=True)
        except Exception as e: print(f"Error: {e}"); time.sleep(5)
