import telebot
from telebot import types
import json
import time
import threading
from datetime import datetime, timedelta
import config
import database as db
from admin_panel import AdminPanel
from utils.decorators import check_limit, check_banned, maintenance_check

# Initialize bot
bot = telebot.TeleBot(config.BOT_TOKEN)
admin_panel = AdminPanel(bot)

# User states storage
user_states = {}

# Initialize database
db.init_database()

print("""
╔══════════════════════════════════════╗
║     🌟 BRONX OSINT BOT V1.0 🌟     ║
║     👑 Created by BRONX_ULTRA      ║
║     🚀 Bot Started Successfully     ║
║     ✅ All Systems Online           ║
╚══════════════════════════════════════╝
""")

# ==================== START COMMAND ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    first_name = message.from_user.first_name or "User"
    
    # Register user if new
    db.register_user(user_id, username, first_name)
    
    # Welcome message with inline buttons
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Create stylish buttons
    buttons = [
        types.InlineKeyboardButton("📱 NUMBER INFO", callback_data="menu_number_info"),
        types.InlineKeyboardButton("🆔 AADHAR INFO", callback_data="menu_aadhar_info"),
        types.InlineKeyboardButton("🚗 VEHICLE INFO", callback_data="menu_vehicle_info"),
        types.InlineKeyboardButton("🏦 IFSC INFO", callback_data="menu_ifsc_info"),
        types.InlineKeyboardButton("📞 TG TO NUMBER", callback_data="menu_telegram_info"),
        types.InlineKeyboardButton("🎮 FREE FIRE INFO", callback_data="menu_freefire_info"),
        types.InlineKeyboardButton("📮 PINCODE INFO", callback_data="menu_pincode_info"),
        types.InlineKeyboardButton("📱 IMEI INFO", callback_data="menu_imei_info"),
        types.InlineKeyboardButton("🌐 IP INFO", callback_data="menu_ip_info"),
        types.InlineKeyboardButton("📸 INSTAGRAM INFO", callback_data="menu_instagram_info"),
        types.InlineKeyboardButton("🪪 AADHAR RATION", callback_data="menu_aadhar_ration"),
        types.InlineKeyboardButton("💳 BUY PREMIUM", callback_data="show_plans"),
        types.InlineKeyboardButton("ℹ️ HELP", callback_data="help_info")
    ]
    
    markup.add(*buttons)
    
    welcome_text = f"""
🌟 *WELCOME TO BRONX OSINT BOT* 🌟

━━━━━━━━━━━━━━━━━━━━━━
👤 *User:* {first_name}
🆔 *ID:* `{user_id}`
📊 *Status:* {'🟢 Active' if not db.is_banned(user_id) else '🔴 Banned'}
🔍 *Remaining:* {db.get_remaining_searches(user_id)}
━━━━━━━━━━━━━━━━━━━━━━

🔰 *Select a feature from below:*
    """
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== HELP COMMAND ====================
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📚 *BRONX OSINT BOT HELP*

━━━━━━━━━━━━━━━━━━━━━━

🔰 *Available Features:*
• 📱 Number Info - Get mobile number details
• 🆔 Aadhar Info - Get Aadhar card details
• 🚗 Vehicle Info - Get RC details
• 🏦 IFSC Info - Get bank details
• 📞 TG to Number - Telegram ID to number
• 🎮 Free Fire Info - Get FF account details
• 📮 Pincode Info - Get area details
• 📱 IMEI Info - Get device details
• 🌐 IP Info - Get IP address details
• 📸 Instagram Info - Instagram to number
• 🪪 Aadhar Ration - Get ration card details

━━━━━━━━━━━━━━━━━━━━━━

💳 *Premium Plans Available*
👑 *Admin:@BRONX_ULTRA*

━━━━━━━━━━━━━━━━━━━━━━
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏠 BACK TO MENU", callback_data="back_to_menu"))
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown", reply_markup=markup)

# ==================== MENU HANDLERS ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def menu_handler(call):
    user_id = call.from_user.id
    
    if db.is_banned(user_id):
        bot.answer_callback_query(call.id, "❌ You are banned from using this bot!", show_alert=True)
        return
    
    if db.is_maintenance_mode():
        bot.answer_callback_query(call.id, "🔧 Bot is under maintenance!", show_alert=True)
        return
    
    feature_map = {
        'menu_number_info': '📱 NUMBER INFO',
        'menu_aadhar_info': '🆔 AADHAR INFO',
        'menu_vehicle_info': '🚗 VEHICLE INFO',
        'menu_ifsc_info': '🏦 IFSC INFO',
        'menu_telegram_info': '📞 TELEGRAM TO NUMBER',
        'menu_freefire_info': '🎮 FREE FIRE INFO',
        'menu_pincode_info': '📮 PINCODE INFO',
        'menu_imei_info': '📱 IMEI INFO',
        'menu_ip_info': '🌐 IP INFO',
        'menu_instagram_info': '📸 INSTAGRAM INFO',
        'menu_aadhar_ration': '🪪 AADHAR RATION'
    }
    
    feature = call.data
    feature_name = feature_map.get(feature, "Feature")
    
    # Set user state
    user_states[user_id] = feature
    
    # Example messages for each feature
    examples = {
        'menu_number_info': '📱 *Send 10 Digit Mobile Number*\n\n📝 Example: `9876543210`',
        'menu_aadhar_info': '🆔 *Send 12 Digit Aadhar Number*\n\n📝 Example: `393933081942`',
        'menu_vehicle_info': '🚗 *Send Vehicle Number*\n\n📝 Example: `MH02FZ0555`',
        'menu_ifsc_info': '🏦 *Send IFSC Code*\n\n📝 Example: `SBIN0001234`',
        'menu_telegram_info': '📞 *Send Telegram User ID*\n\n📝 Example: `7530266953`',
        'menu_freefire_info': '🎮 *Send Free Fire UID*\n\n📝 Example: `123456789`',
        'menu_pincode_info': '📮 *Send 6 Digit Pincode*\n\n📝 Example: `110001`',
        'menu_imei_info': '📱 *Send 15 Digit IMEI Number*\n\n📝 Example: `357817383506298`',
        'menu_ip_info': '🌐 *Send IP Address*\n\n📝 Example: `8.8.8.8`',
        'menu_instagram_info': '📸 *Send Instagram Username*\n\n📝 Example: `cristiano`',
        'menu_aadhar_ration': '🪪 *Send Mobile Number for Ration*\n\n📝 Example: `701984830542`'
    }
    
    example_text = examples.get(feature, "Send your query")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back_to_menu"))
    
    remaining = db.get_remaining_searches(user_id)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"""
🔰 *{feature_name}*

━━━━━━━━━━━━━━━━━━━━━━

{example_text}

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *Remaining Searches:* {remaining}
        """,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== BACK TO MENU ====================
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
def back_to_menu(call):
    user_id = call.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    send_welcome_from_callback(call)

def send_welcome_from_callback(call):
    user_id = call.from_user.id
    first_name = call.from_user.first_name or "User"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        types.InlineKeyboardButton("📱 NUMBER INFO", callback_data="menu_number_info"),
        types.InlineKeyboardButton("🆔 AADHAR INFO", callback_data="menu_aadhar_info"),
        types.InlineKeyboardButton("🚗 VEHICLE INFO", callback_data="menu_vehicle_info"),
        types.InlineKeyboardButton("🏦 IFSC INFO", callback_data="menu_ifsc_info"),
        types.InlineKeyboardButton("📞 TG TO NUMBER", callback_data="menu_telegram_info"),
        types.InlineKeyboardButton("🎮 FREE FIRE INFO", callback_data="menu_freefire_info"),
        types.InlineKeyboardButton("📮 PINCODE INFO", callback_data="menu_pincode_info"),
        types.InlineKeyboardButton("📱 IMEI INFO", callback_data="menu_imei_info"),
        types.InlineKeyboardButton("🌐 IP INFO", callback_data="menu_ip_info"),
        types.InlineKeyboardButton("📸 INSTAGRAM INFO", callback_data="menu_instagram_info"),
        types.InlineKeyboardButton("🪪 AADHAR RATION", callback_data="menu_aadhar_ration"),
        types.InlineKeyboardButton("💳 BUY PREMIUM", callback_data="show_plans"),
        types.InlineKeyboardButton("ℹ️ HELP", callback_data="help_info")
    ]
    
    markup.add(*buttons)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"""
🌟 *WELCOME TO BRONX OSINT BOT* 🌟

━━━━━━━━━━━━━━━━━━━━━━
👤 *User:* {first_name}
🆔 *ID:* `{user_id}`
🔍 *Remaining:* {db.get_remaining_searches(user_id)}
━━━━━━━━━━━━━━━━━━━━━━

🔰 *Select a feature from below:*
        """,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== HELP INFO CALLBACK ====================
@bot.callback_query_handler(func=lambda call: call.data == 'help_info')
def help_callback(call):
    help_text = """
📚 *BRONX OSINT BOT HELP*

━━━━━━━━━━━━━━━━━━━━━━

🔰 *Available Features:*
• 📱 Number Info - Get mobile number details
• 🆔 Aadhar Info - Get Aadhar card details
• 🚗 Vehicle Info - Get RC details
• 🏦 IFSC Info - Get bank details
• 📞 TG to Number - Telegram ID to number
• 🎮 Free Fire Info - Get FF account details
• 📮 Pincode Info - Get area details
• 📱 IMEI Info - Get device details
• 🌐 IP Info - Get IP address details
• 📸 Instagram Info - Instagram to number
• 🪪 Aadhar Ration - Get ration card details

━━━━━━━━━━━━━━━━━━━━━━

💳 *Premium Plans Available*
👑 *Contact: @BRONX_ULTRA*

━━━━━━━━━━━━━━━━━━━━━━
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏠 BACK TO MENU", callback_data="back_to_menu"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=help_text,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== MESSAGE HANDLER ====================
@bot.message_handler(func=lambda message: True)
@maintenance_check
@check_banned
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Check for admin commands
    if text.startswith('/admin') or text in ['/stats', '/vip_list', '/ping']:
        if str(user_id) == str(config.ADMIN_ID) or db.is_admin(user_id):
            admin_panel.process_command(message)
            return
    
    # Check if user is in any feature state
    if user_id in user_states:
        feature = user_states[user_id]
        process_feature_request(message, feature)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🌟 START BOT", callback_data="back_to_menu"))
        
        bot.reply_to(
            message, 
            "🏠 *Please use /start to begin*", 
            parse_mode="Markdown",
            reply_markup=markup
        )

# ==================== FEATURE PROCESSING ====================
@check_limit
def process_feature_request(message, feature):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Feature to handler mapping
    feature_handlers = {
        'menu_number_info': 'number_info',
        'menu_aadhar_info': 'aadhar_info',
        'menu_vehicle_info': 'vehicle_info',
        'menu_ifsc_info': 'ifsc_info',
        'menu_telegram_info': 'telegram_info',
        'menu_freefire_info': 'freefire_info',
        'menu_pincode_info': 'pincode_info',
        'menu_imei_info': 'imei_info',
        'menu_ip_info': 'ip_info',
        'menu_instagram_info': 'instagram_info',
        'menu_aadhar_ration': 'aadhar_ration'
    }
    
    handler_name = feature_handlers.get(feature)
    
    if handler_name:
        # Decrement search count
        if not db.decrement_search(user_id):
            handle_limit_exceeded(message)
            return
        
        # Import and call the appropriate handler
        try:
            import importlib
            handler = importlib.import_module(f'handlers.{handler_name}')
            
            # Log the search
            db.log_search(user_id, handler_name, text)
            
            # Process the request
            handler.process(bot, message)
            
            # Clear state after processing
            if user_id in user_states:
                del user_states[user_id]
                
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")
    else:
        bot.reply_to(message, "🔧 Feature not available")

# ==================== LIMIT EXCEEDED HANDLER ====================
def handle_limit_exceeded(message):
    user_id = message.from_user.id
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    plans = [
        types.InlineKeyboardButton("💎 5 DAYS - ₹50 (50 Searches)", callback_data="plan_5days"),
        types.InlineKeyboardButton("💎 10 DAYS - ₹100 (100 Searches)", callback_data="plan_10days"),
        types.InlineKeyboardButton("💎 20 DAYS - ₹200 (200 Searches)", callback_data="plan_20days"),
        types.InlineKeyboardButton("💎 30 DAYS - ₹300 (Unlimited)", callback_data="plan_30days"),
        types.InlineKeyboardButton("💎 60 DAYS - ₹600 (Unlimited)", callback_data="plan_60days"),
        types.InlineKeyboardButton("💎 100 DAYS - ₹999 (Unlimited 24/7)", callback_data="plan_100days"),
        types.InlineKeyboardButton("👑 LIFETIME - ₹3000 (Unlimited)", callback_data="plan_lifetime"),
        types.InlineKeyboardButton("📞 CONTACT OWNER", url="https://t.me/BRONX_ULTRA")
    ]
    
    markup.add(*plans)
    
    bot.send_message(
        message.chat.id,
        """
❌ *LIMIT EXCEEDED!* ❌

━━━━━━━━━━━━━━━━━━━━━━

😔 *Your search limit is over!*

🔒 Please upgrade your plan to continue using the bot.

📞 *Contact Owner:* @BRONX_ULTRA

━━━━━━━━━━━━━━━━━━━━━━

💳 *Available Plans:*
        """,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== PLAN SYSTEM ====================
@bot.callback_query_handler(func=lambda call: call.data == 'show_plans')
def show_plans(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    plans = [
        ("💎 5 DAYS - ₹50 (50 Searches)", "plan_5days"),
        ("💎 10 DAYS - ₹100 (100 Searches)", "plan_10days"),
        ("💎 20 DAYS - ₹200 (200 Searches)", "plan_20days"),
        ("💎 30 DAYS - ₹300 (Unlimited)", "plan_30days"),
        ("💎 60 DAYS - ₹600 (Unlimited)", "plan_60days"),
        ("💎 100 DAYS - ₹999 (Unlimited 24/7)", "plan_100days"),
        ("👑 LIFETIME - ₹3000 (Unlimited)", "plan_lifetime"),
        ("🔙 BACK TO MENU", "back_to_menu")
    ]
    
    for text, callback in plans:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="""
💳 *PREMIUM PLANS* 💳

━━━━━━━━━━━━━━━━━━━━━━

🌟 *Choose your plan:*

💎 *5 Days* - ₹50
   ↳ 50 Searches Limit

💎 *10 Days* - ₹100
   ↳ 100 Searches Limit

💎 *20 Days* - ₹200
   ↳ 200 Searches Limit

💎 *30 Days* - ₹300
   ↳ Unlimited Searches

💎 *60 Days* - ₹600
   ↳ Unlimited Searches

💎 *100 Days* - ₹999
   ↳ Unlimited 24/7

👑 *Lifetime* - ₹3000
   ↳ No Limit, Unlimited

━━━━━━━━━━━━━━━━━━━━━━
📞 *Contact:* @BRONX_ULTRA
        """,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('plan_'))
def plan_details(call):
    plan_data = {
        'plan_5days': {'name': '5 Days Plan', 'price': '₹50', 'searches': '50', 'days': 5},
        'plan_10days': {'name': '10 Days Plan', 'price': '₹100', 'searches': '100', 'days': 10},
        'plan_20days': {'name': '20 Days Plan', 'price': '₹200', 'searches': '200', 'days': 20},
        'plan_30days': {'name': '30 Days Plan', 'price': '₹300', 'searches': 'Unlimited', 'days': 30},
        'plan_60days': {'name': '60 Days Plan', 'price': '₹600', 'searches': 'Unlimited', 'days': 60},
        'plan_100days': {'name': '100 Days Plan', 'price': '₹999', 'searches': 'Unlimited 24/7', 'days': 100},
        'plan_lifetime': {'name': 'Lifetime Plan', 'price': '₹3000', 'searches': 'Unlimited', 'days': 'Lifetime'}
    }
    
    plan = plan_data.get(call.data)
    
    if plan:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💳 BUY NOW", url="https://t.me/BRONX_ULTRA"))
        markup.add(types.InlineKeyboardButton("🔙 BACK TO PLANS", callback_data="show_plans"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"""
📋 *PLAN DETAILS*

━━━━━━━━━━━━━━━━━━━━━━

📌 *Plan:* {plan['name']}
💰 *Price:* {plan['price']}
🔍 *Searches:* {plan['searches']}
⏰ *Duration:* {plan['days']} Days

━━━━━━━━━━━━━━━━━━━━━━

✨ *Benefits:*
✅ Full Access to All Features
✅ Priority Support
✅ Fast Results
✅ 24/7 Availability
✅ No Ads

━━━━━━━━━━━━━━━━━━━━━━
📞 Contact @BRONX_ULTRA to purchase
            """,
            parse_mode="Markdown",
            reply_markup=markup
        )

# ==================== RUN BOT ====================
if __name__ == "__main__":
    # Start admin panel monitoring in separate thread
    admin_thread = threading.Thread(target=admin_panel.start_monitoring)
    admin_thread.daemon = True
    admin_thread.start()
    
    # Start bot polling
    while True:
        try:
            print("🔄 Bot polling started...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
