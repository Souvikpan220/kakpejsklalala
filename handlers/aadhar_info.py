from utils.api_handler import call, fmt

def process(bot, msg):
    t = msg.text.strip()
    if not t.isdigit() or len(t) != 12:
        bot.reply_to(msg, "❌ Send 12-digit Aadhar!\nExample: `393933081942`", parse_mode="Markdown")
        return
    m = bot.reply_to(msg, "🔍 *Searching...*", parse_mode="Markdown")
    r = call('aadhar_info', t)
    bot.edit_message_text(fmt(r, "🆔 AADHAR INFO"), msg.chat.id, m.message_id, parse_mode="Markdown")
