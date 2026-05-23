from utils.api_handler import call, fmt

def process(bot, msg):
    t = msg.text.strip()
    if not t.isdigit():
        bot.reply_to(msg, "❌ Send FF UID!\nExample: `123456789`", parse_mode="Markdown")
        return
    m = bot.reply_to(msg, "🔍 *Searching...*", parse_mode="Markdown")
    r = call('freefire_info', t)
    bot.edit_message_text(fmt(r, "🎮 FREE FIRE INFO"), msg.chat.id, m.message_id, parse_mode="Markdown")
