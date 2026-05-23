BOT_TOKEN = "8798121433:AAHWaM8fMXWmT4rtUHbAik22YODehyjHllo"
ADMIN_ID = "7530266953"
API_BASE = "https://osint-api-website-bronx.vercel.app/api"
API_KEY = "op"

APIS = {
    'number_info': f'{API_BASE}/key-bronx/number?key={API_KEY}&num=',
    'aadhar_info': f'{API_BASE}/key-bronx/aadhar?key={API_KEY}&num=',
    'vehicle_info': f'{API_BASE}/custom/rc-details?key={API_KEY}&ca_number=',
    'ifsc_info': f'{API_BASE}/key-bronx/ifsc?key={API_KEY}&ifsc=',
    'telegram_info': f'{API_BASE}/custom/telegram-scan?key={API_KEY}&id=',
    'freefire_info': f'{API_BASE}/key-bronx/ff?key={API_KEY}&uid=',
    'pincode_info': f'{API_BASE}/key-bronx/pincode?key={API_KEY}&pin=',
    'imei_info': f'{API_BASE}/key-bronx/imei?key={API_KEY}&imei=',
    'ip_info': f'{API_BASE}/key-bronx/ip?key={API_KEY}&ip=',
    'instagram_info': f'{API_BASE}/key-bronx/insta?key={API_KEY}&username=',
    'aadhar_ration': f'{API_BASE}/key-bronx/adharration?key={API_KEY}&num=',
    'extra_1': '', 'extra_2': '', 'extra_3': '', 'extra_4': '', 'extra_5': '',
    'extra_6': '', 'extra_7': '', 'extra_8': '', 'extra_9': '', 'extra_10': '',
}

DB_PATH = 'bronx.db'
LIMIT = 3
