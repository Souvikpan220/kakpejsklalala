
## 5. **utils/decorators.py** - Decorators

```python
from functools import wraps
import database as db
from telebot import types

def check_limit(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        
        # VIP users have unlimited access
        if db.is_vip(user_id):
            return func(message, *args, **kwargs)
        
        # Check remaining searches
        remaining = db.get_remaining_searches(user_id)
        
        if isinstance(remaining, int) and remaining <= 0:
            # Import here to avoid circular import
            from bot import handle_limit_exceeded
            handle_limit_exceeded(message)
            return
        
        return func(message, *args, **kwargs)
    return wrapper

def check_banned(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        
        if db.is_banned(user_id):
            # Try to reply if possible
            try:
                from bot import bot
                bot.reply_to(message, """
🚫 *YOU ARE BANNED!*

━━━━━━━━━━━━━━━━━━━━━━

❌ You are banned from using this bot.

📞 Contact @BRONX_ULTRA for appeal.

━━━━━━━━━━━━━━━━━━━━━━
                """, parse_mode="Markdown")
            except:
                pass
            return
        
        return func(message, *args, **kwargs)
    return wrapper

def maintenance_check(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if db.is_maintenance_mode():
            try:
                from bot import bot
                bot.reply_to(
                    message,
                    """
🔧 *BOT UNDER MAINTENANCE* 🔧

━━━━━━━━━━━━━━━━━━━━━━

The bot is currently under maintenance.
Please try again later.

📞 Contact @BRONX_ULTRA for info

━━━━━━━━━━━━━━━━━━━━━━
                    """,
                    parse_mode="Markdown"
                )
            except:
                pass
            return
        
        return func(message, *args, **kwargs)
    return wrapper
