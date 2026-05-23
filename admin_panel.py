import telebot
from telebot import types
import database as db
import config
from datetime import datetime, timedelta
import time

class AdminPanel:
    def __init__(self, bot):
        self.bot = bot
    
    def process_command(self, message):
        user_id = message.from_user.id
        text = message.text
        parts = text.split()
        command = parts[0].lower() if parts else ""
        
        if str(user_id) != str(config.ADMIN_ID) and not db.is_admin(user_id):
            return
        
        if command == '/admin' and len(parts) > 1:
            action = parts[1].lower()
            
            if action == 'limit' and len(parts) >= 4:
                target_id = int(parts[2])
                limit = int(parts[3])
                self.set_limit(message, target_id, limit)
            
            elif action == 'ban' and len(parts) >= 3:
                target_id = int(parts[2])
                self.ban_user(message, target_id)
            
            elif action == 'unban' and len(parts) >= 3:
                target_id = int(parts[2])
                self.unban_user(message, target_id)
            
            elif action == 'broadcast' and len(parts) >= 3:
                broadcast_msg = ' '.join(parts[2:])
                self.broadcast(message, broadcast_msg)
            
            elif action == 'pm' and len(parts) >= 4:
                target_id = int(parts[2])
                pm_msg = ' '.join(parts[3:])
                self.send_pm(message, target_id, pm_msg)
            
            elif action == 'vip' and len(parts) >= 4:
                target_id = int(parts[2])
                duration_str = parts[3]
                self.set_vip(message, target_id, duration_str)
            
            elif action == 'vip' and len(parts) >= 3:
                target_id = int(parts[2])
                self.set_vip(message, target_id, '30')
            
            elif action == 'maintenance':
                self.toggle_maintenance(message)
            
            elif action == 'vip_list':
                self.show_vip_list(message)
            
            elif action == 'stats':
                self.show_stats(message)
            
            elif action == 'add' and len(parts) >= 3:
                target_id = int(parts[2])
                username = parts[3] if len(parts) > 3 else "Unknown"
                self.add_admin_user(message, target_id, username)
            
            elif action == 'remove' and len(parts) >= 3:
                target_id = int(parts[2])
                self.remove_admin_user(message, target_id)
            
            elif action == 'ping':
                self.ping(message)
            
            elif action == 'status':
                self.show_status(message)
            
            elif action == 'admin_list':
                self.show_admin_list(message)
            
            elif action == 'user_info' and len(parts) >= 3:
                target_id = int(parts[2])
                self.show_user_info(message, target_id)
    
    def set_limit(self, message, target_id, limit):
        db.set_user_limit(target_id, limit)
        self.bot.reply_to(message, f"""
✅ *Limit Updated!*
👤 User: `{target_id}`
🔍 New Limit: `{limit}`
        """, parse_mode="Markdown")
    
    def ban_user(self, message, target_id):
        db.ban_user(target_id)
        self.bot.reply_to(message, f"🚫 *User Banned!*\n👤 ID: `{target_id}`", parse_mode="Markdown")
        try:
            self.bot.send_message(target_id, "❌ You have been banned!\nContact @BRONX_ULTRA", parse_mode="Markdown")
        except: pass
    
    def unban_user(self, message, target_id):
        db.unban_user(target_id)
        self.bot.reply_to(message, f"✅ *User Unbanned!*\n👤 ID: `{target_id}`", parse_mode="Markdown")
        try:
            self.bot.send_message(target_id, "✅ You have been unbanned!\nUse /start", parse_mode="Markdown")
        except: pass
    
    def broadcast(self, message, broadcast_msg):
        users = db.get_all_users()
        success, failed = 0, 0
        
        self.bot.reply_to(message, f"📢 *Broadcasting to {len(users)} users...*", parse_mode="Markdown")
        
        for user in users:
            try:
                self.bot.send_message(user[0], f"📢 *BROADCAST*\n\n{broadcast_msg}\n\n🤖 @BRONX_ULTRA", parse_mode="Markdown")
                success += 1
            except: failed += 1
        
        self.bot.reply_to(message, f"""
📊 *Broadcast Complete*
✅ Success: {success}
❌ Failed: {failed}
        """, parse_mode="Markdown")
    
    def send_pm(self, message, target_id, pm_msg):
        try:
            self.bot.send_message(target_id, f"📨 *Admin Message*\n\n{pm_msg}\n\n🤖 @BRONX_ULTRA", parse_mode="Markdown")
            self.bot.reply_to(message, f"✅ PM sent to `{target_id}`", parse_mode="Markdown")
        except Exception as e:
            self.bot.reply_to(message, f"❌ Failed: {e}")
    
    def set_vip(self, message, target_id, duration_str):
        try:
            duration = int(duration_str.replace('d', ''))
            db.set_vip(target_id, duration)
            expiry = datetime.now() + timedelta(days=duration)
            
            try:
                self.bot.send_message(target_id, f"""
🎉 *CONGRATULATIONS!*

👤 ID: `{target_id}`
👑 Status: VIP
⏰ Duration: {duration} Days
📅 Expires: {expiry.strftime('%Y-%m-%d')}

✨ Unlimited access activated!
                """, parse_mode="Markdown")
            except: pass
            
            self.bot.reply_to(message, f"""
✅ *VIP Granted!*
👤 User: `{target_id}`
⏰ Duration: {duration} Days
📅 Expires: {expiry.strftime('%Y-%m-%d')}
            """, parse_mode="Markdown")
        except Exception as e:
            self.bot.reply_to(message, f"❌ Error: {e}\nFormat: /admin vip ID 5d")
    
    def toggle_maintenance(self, message):
        is_on = db.toggle_maintenance()
        status = "🔴 ON" if is_on else "🟢 OFF"
        self.bot.reply_to(message, f"🔧 *Maintenance:* {status}", parse_mode="Markdown")
    
    def show_vip_list(self, message):
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.user_id, u.username, u.first_name, v.duration_days, v.expiry_date
            FROM users u JOIN vip_users v ON u.user_id = v.user_id
            WHERE u.is_vip = 1
        ''')
        vips = cursor.fetchall()
        conn.close()
        
        if not vips:
            self.bot.reply_to(message, "👑 No VIP users found", parse_mode="Markdown")
            return
        
        vip_text = "👑 *VIP USERS*\n\n"
        for vip in vips:
            vip_text += f"👤 `{vip[0]}` - {vip[2]} (@{vip[1]}) | {vip[3]}D | Exp: {vip[4]}\n"
        
        self.bot.reply_to(message, vip_text, parse_mode="Markdown")
    
    def show_stats(self, message):
        total = db.get_total_users()
        vips = db.get_total_vip_users()
        features = db.get_feature_stats()
        
        stats = f"""
📊 *BOT STATS*

👥 Users: {total}
👑 VIPs: {vips}

🔍 *Features Used:*
"""
        for f in features:
            stats += f"• {f[0]}: {f[1]}\n"
        
        self.bot.reply_to(message, stats, parse_mode="Markdown")
    
    def show_status(self, message):
        features = db.get_feature_stats()
        status_text = "📊 *FEATURE STATUS*\n\n"
        
        for f in features:
            status_text += f"✅ {f[0]}: {f[1]} searches\n"
        
        self.bot.reply_to(message, status_text, parse_mode="Markdown")
    
    def show_admin_list(self, message):
        admins = db.get_admin_list()
        admin_text = "👑 *ADMIN LIST*\n\n"
        
        for admin in admins:
            admin_text += f"👤 `{admin[0]}` - @{admin[1]}\n"
        
        self.bot.reply_to(message, admin_text, parse_mode="Markdown")
    
    def add_admin_user(self, message, target_id, username):
        db.add_admin(target_id, username, message.from_user.id)
        self.bot.reply_to(message, f"✅ Admin Added: `{target_id}` - @{username}", parse_mode="Markdown")
    
    def remove_admin_user(self, message, target_id):
        db.remove_admin(target_id)
        self.bot.reply_to(message, f"✅ Admin Removed: `{target_id}`", parse_mode="Markdown")
    
    def ping(self, message):
        start = time.time()
        msg = self.bot.reply_to(message, "🏓")
        end = time.time()
        ping_time = round((end - start) * 1000)
        self.bot.edit_message_text(f"🏓 Pong! `{ping_time}ms`\n✅ Bot Online", message.chat.id, msg.message_id, parse_mode="Markdown")
    
    def show_user_info(self, message, user_id):
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            self.bot.reply_to(message, "❌ User not found!")
            return
        
        info = f"""
👤 *USER INFO*

🆔 ID: `{user[0]}`
📛 Name: {user[2]}
👤 Username: @{user[1]}
🔍 Searches: {user[3]}/{user[4]}
🚫 Banned: {'Yes' if user[5] else 'No'}
👑 VIP: {'Yes' if user[6] else 'No'}
📅 VIP Expiry: {user[7] or 'N/A'}
📅 Joined: {user[8]}
        """
        self.bot.reply_to(message, info, parse_mode="Markdown")
    
    def start_monitoring(self):
        """Background monitoring for expired VIPs"""
        while True:
            time.sleep(3600)
            self.check_expired_vips()
    
    def check_expired_vips(self):
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_vip = 0 WHERE is_vip = 1 AND vip_expiry < DATE('now')")
        conn.commit()
        conn.close()
