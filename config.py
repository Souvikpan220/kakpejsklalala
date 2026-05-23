# Bot Configuration
BOT_TOKEN = "8798121433:AAHWaM8fMXWmT4rtUHbAik22YODehyjHllo"
ADMIN_ID = "6840524720"  # Apna Telegram ID daalo

# API Base URL
API_BASE_URL = "https://osint-api-website-bronx.vercel.app/api"
API_KEY = "op"

# API Endpoints Configuration
API_ENDPOINTS = {
    'number_info': f'{API_BASE_URL}/key-bronx/number?key={API_KEY}&num=',
    'aadhar_info': f'{API_BASE_URL}/key-bronx/aadhar?key={API_KEY}&num=',
    'vehicle_info': f'{API_BASE_URL}/custom/rc-details?key={API_KEY}&ca_number=',
    'ifsc_info': f'{API_BASE_URL}/key-bronx/ifsc?key={API_KEY}&ifsc=',
    'telegram_info': f'{API_BASE_URL}/custom/telegram-scan?key={API_KEY}&id=',
    'freefire_info': f'{API_BASE_URL}/key-bronx/ff?key={API_KEY}&uid=',
    'pincode_info': f'{API_BASE_URL}/key-bronx/pincode?key={API_KEY}&pin=',
    'imei_info': f'{API_BASE_URL}/key-bronx/imei?key={API_KEY}&imei=',
    'ip_info': f'{API_BASE_URL}/key-bronx/ip?key={API_KEY}&ip=',
    'instagram_info': f'{API_BASE_URL}/key-bronx/insta?key={API_KEY}&username=',
    'aadhar_ration': f'{API_BASE_URL}/key-bronx/adharration?key={API_KEY}&num=',
    # Extra API slots for future use
    'bgmi_info': f'{API_BASE_URL}/key-bronx/bgmi?key={API_KEY}&id=',
    'family_info': f'{API_BASE_URL}/key-bronx/family?key={API_KEY}&id=',
    'advance_info': f'{API_BASE_URL}/key-bronx/advance?key={API_KEY}&query=',
    # Extra API slots (10 additional)
    'extra_api_1': '',
    'extra_api_2': '',
    'extra_api_3': '',
    'extra_api_4': '',
    'extra_api_5': '',
    'extra_api_6': '',
    'extra_api_7': '',
    'extra_api_8': '',
    'extra_api_9': '',
    'extra_api_10': '',
}

# Database Configuration
DATABASE_PATH = 'bronx_osint.db'

# Default Limits
DEFAULT_SEARCH_LIMIT = 3
