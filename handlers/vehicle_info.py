from utils.api_handler import make_api_request, format_response

def process(bot, message):
    text = message.text.strip().upper()
    
    if not text:
        bot.reply_to(message, "❌ Please send vehicle number!\n📝 Example: `MH02FZ0555`", parse_mode="Markdown")
        return
    
    processing_msg = bot.reply_to(message, "🔍 *Fetching Vehicle Details...* 🚗", parse_mode="Markdown")
    result = make_api_request('vehicle_info', text)
    formatted = format_response(result, "🚗 VEHICLE INFO")
    
    bot.edit_message_text(formatted, chat_id=message.chat.id, message_id=processing_msg.message_id, parse_mode="Markdown")
