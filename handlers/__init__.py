# handlers/__init__.py
cat > handlers/__init__.py << 'EOF'
EOF

# handlers/number_info.py
cat > handlers/number_info.py << 'EOF'
from utils.api_handler import make_api_request, format_response

def process(bot, message):
    text = message.text.strip()
    if not text.isdigit() or len(text) != 10:
        bot.reply_to(message, "❌ *Invalid Number!*\n\nSend 10-digit mobile number.\nExample: `9876543210`", parse_mode="Markdown")
        return
    processing_msg = bot.reply_to(message, "🔍 *Searching Number Info...*", parse_mode="Markdown")
    result = make_api_request('number_info', text)
    formatted = format_response(result, "📱 NUMBER INFO")
    bot.edit_message_text(formatted, chat_id=message.chat.id, message_id=processing_msg.message_id, parse_mode="Markdown")
EOF
