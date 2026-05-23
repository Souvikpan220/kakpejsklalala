from utils.api_handler import make_api_request, format_response

def process(bot, message):
    text = message.text.strip()
    
    if not text.isdigit() or len(text) != 6:
        bot.reply_to(message, "❌ Please send 6-digit pincode!\n📝 Example: `110001`", parse_mode="Markdown")
        return
    
    processing_msg = bot.reply_to(message, "🔍 *Fetching Pincode Info...* 📮", parse_mode="Markdown")
    result = make_api_request('pincode_info', text)
    formatted = format_response(result, "📮 PINCODE INFO")
    
    bot.edit_message_text(formatted, chat_id=message.chat.id, message_id=processing_msg.message_id, parse_mode="Markdown")
