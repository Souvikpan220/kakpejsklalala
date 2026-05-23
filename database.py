import sqlite3
from datetime import datetime, timedelta
import config

def con():
    return sqlite3.connect(config.DB_PATH, check_same_thread=False)

def init_database():
    c = con()
    cur = c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, uname TEXT, fname TEXT, cnt INTEGER DEFAULT 0, lim INTEGER DEFAULT 3, ban INTEGER DEFAULT 0, vip INTEGER DEFAULT 0, vexp DATE, jdate DATE DEFAULT CURRENT_DATE)")
    cur.execute("CREATE TABLE IF NOT EXISTS admins (uid INTEGER PRIMARY KEY, uname TEXT, added_by INTEGER, adate DATE DEFAULT CURRENT_DATE)")
    cur.execute("CREATE TABLE IF NOT EXISTS vips (uid INTEGER PRIMARY KEY, dur INTEGER, sdate DATE, edate DATE, by_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, feat TEXT, query TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS fstats (feat TEXT PRIMARY KEY, total INTEGER DEFAULT 0, last DATETIME)")
    cur.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, val TEXT)")
    cur.execute("INSERT OR IGNORE INTO settings VALUES ('maint','0')")
    cur.execute("INSERT OR IGNORE INTO admins VALUES (?,?,?,DATE('now'))", (config.ADMIN_ID, 'BRONX_ULTRA', config.ADMIN_ID))
    c.commit()
    c.close()

def reg(uid, uname, fname):
    c = con()
    c.cursor().execute("INSERT OR IGNORE INTO users (uid,uname,fname) VALUES (?,?,?)", (uid, uname, fname))
    c.commit()
    c.close()

def banned(uid):
    c = con()
    r = c.cursor().execute("SELECT ban FROM users WHERE uid=?", (uid,)).fetchone()
    c.close()
    return r and r[0]==1

def is_vip(uid):
    c = con()
    r = c.cursor().execute("SELECT vip FROM users WHERE uid=? AND vip=1 AND (vexp IS NULL OR vexp>=DATE('now'))", (uid,)).fetchone()
    c.close()
    return r is not None

def rem(uid):
    if is_vip(uid): return "♾️ Unlimited"
    c = con()
    r = c.cursor().execute("SELECT lim-cnt FROM users WHERE uid=?", (uid,)).fetchone()
    c.close()
    return r[0] if r else 0

def dec(uid):
    if is_vip(uid): return True
    c = con()
    cur = c.cursor()
    r = cur.execute("SELECT lim-cnt FROM users WHERE uid=?", (uid,)).fetchone()
    if r and r[0]>0:
        cur.execute("UPDATE users SET cnt=cnt+1 WHERE uid=?", (uid,))
        c.commit()
        c.close()
        return True
    c.close()
    return False

def set_lim(uid, lim):
    c = con()
    c.cursor().execute("UPDATE users SET lim=?, cnt=0 WHERE uid=?", (lim, uid))
    c.commit()
    c.close()

def ban(uid):
    c = con()
    c.cursor().execute("UPDATE users SET ban=1 WHERE uid=?", (uid,))
    c.commit()
    c.close()

def unban(uid):
    c = con()
    c.cursor().execute("UPDATE users SET ban=0 WHERE uid=?", (uid,))
    c.commit()
    c.close()

def set_vip(uid, dur):
    c = con()
    cur = c.cursor()
    ed = datetime.now() + timedelta(days=dur)
    cur.execute("UPDATE users SET vip=1, vexp=?, cnt=0, lim=99999 WHERE uid=?", (ed.strftime('%Y-%m-%d'), uid))
    cur.execute("INSERT OR REPLACE INTO vips VALUES (?,?,DATE('now'),?,?)", (uid, dur, ed.strftime('%Y-%m-%d'), config.ADMIN_ID))
    c.commit()
    c.close()

def log(uid, feat, query):
    c = con()
    cur = c.cursor()
    cur.execute("INSERT INTO logs (uid,feat,query) VALUES (?,?,?)", (uid, feat, query))
    cur.execute("INSERT INTO fstats (feat,total,last) VALUES (?,1,DATETIME('now')) ON CONFLICT(feat) DO UPDATE SET total=total+1, last=DATETIME('now')", (feat,))
    c.commit()
    c.close()

def total_users():
    c = con()
    r = c.cursor().execute("SELECT COUNT(*) FROM users").fetchone()[0]
    c.close()
    return r

def total_vips():
    c = con()
    r = c.cursor().execute("SELECT COUNT(*) FROM users WHERE vip=1").fetchone()[0]
    c.close()
    return r

def fstats_data():
    c = con()
    r = c.cursor().execute("SELECT * FROM fstats ORDER BY total DESC").fetchall()
    c.close()
    return r

def all_users():
    c = con()
    r = c.cursor().execute("SELECT uid,uname,fname FROM users").fetchall()
    c.close()
    return r

def admin_list():
    c = con()
    r = c.cursor().execute("SELECT * FROM admins").fetchall()
    c.close()
    return r

def is_admin(uid):
    c = con()
    r = c.cursor().execute("SELECT * FROM admins WHERE uid=?", (uid,)).fetchone()
    c.close()
    return r is not None

def add_admin(uid, uname, by_id):
    c = con()
    c.cursor().execute("INSERT OR IGNORE INTO admins VALUES (?,?,?,DATE('now'))", (uid, uname, by_id))
    c.commit()
    c.close()

def rem_admin(uid):
    c = con()
    c.cursor().execute("DELETE FROM admins WHERE uid=? AND uid!=?", (uid, config.ADMIN_ID))
    c.commit()
    c.close()

def toggle_maint():
    c = con()
    cur = c.cursor()
    cur.execute("SELECT val FROM settings WHERE key='maint'")
    curr = cur.fetchone()[0]
    new = '0' if curr=='1' else '1'
    cur.execute("UPDATE settings SET val=? WHERE key='maint'", (new,))
    c.commit()
    c.close()
    return new=='1'

def is_maint():
    c = con()
    r = c.cursor().execute("SELECT val FROM settings WHERE key='maint'").fetchone()
    c.close()
    return r and r[0]=='1'
