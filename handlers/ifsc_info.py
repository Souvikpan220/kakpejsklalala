from utils.api_handler import make_api_request, format_response

def process(bot, message):
    text = message.text.strip().upper()
    
    processing_msg = bot.reply_to(message, "🔍 *Fetching Bank Details...* 🏦", parse_mode="Markdown")
    result = make_api_request('ifsc_info', text)
    formatted = format_response(result, "🏦 IFSC INFO")
    
    bot.edit_message_text(formatted, chat_id=message.chat.id, message_id=processing_msg.message_id, parse_mode="Markdown")
