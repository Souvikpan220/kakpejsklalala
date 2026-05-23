import requests, json, config

def call(feature, query):
    url = config.APIS.get(feature, '')
    if not url: return {"error": "API not configured"}
    try:
        r = requests.get(f"{url}{query}", headers={'User-Agent':'BRONX-BOT'}, timeout=15)
        if r.status_code == 200:
            return r.json()
        return {"error": f"Status {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def fmt(data, name):
    if not data: return "❌ *No Data*"
    if 'error' in data: return f"❌ *Error*\n{data['error']}"
    try:
        j = json.dumps(data, indent=2, ensure_ascii=False)
        if len(j) > 3500: j = j[:3500] + "..."
        return f"✅ *{name}*\n```json\n{j}\n```\n🤖 @BRONX_ULTRA"
    except:
        return f"✅ *{name}*\n{str(data)[:3000]}"
