import time
import datetime
import requests
import os
import urllib3
import threading

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIG ZA KING JABIR ---
TELEGRAM_TOKEN = "8136524092:AAFCmY5hB_yivteemViUW8i7l1GEz10AgPY" 
CHAT_ID = "7992273662" 
SESSION_TARGET = 5 # Wins 5 session inafunga

# --- BRANDED LOGOS ---
PHOTO_SESSION_1 = "https://img.freepik.com/premium-photo/forex-trading-logo-with-letter-j-luxury-gold-theme-morning-sun-background_941600-102.jpg"
PHOTO_SESSION_4 = "https://img.freepik.com/premium-photo/dark-neon-trading-setup-with-glowing-gold-j-logo-digital-currency-concept_941600-410.jpg"
PHOTO_STARTUP = "https://img.freepik.com/premium-photo/professional-trading-logo-gold-j-letter-candlesticks-3d-render_941600-512.jpg"

NORMAL_PAIRS = ["EURUSD", "GBPUSD", "XAUUSD", "USDJPY", "AUDCAD", "EURUSD-OTC", "GBPUSD-OTC"]
SPECIAL_PAIR_S4 = ["AUDJPY"]

SESSIONS = [
    {"start": "06:00", "end": "08:00", "name": "1ST JABIR SESSION", "photo": PHOTO_SESSION_1}, 
    {"start": "14:00", "end": "16:00", "name": "2ND JABIR SESSION", "photo": PHOTO_SESSION_1}, 
    {"start": "18:00", "end": "21:00", "name": "3RD JABIR SESSION", "photo": PHOTO_SESSION_1},
    {"start": "22:00", "end": "01:00", "name": "4TH JABIR SESSION", "photo": PHOTO_SESSION_4}
]

session_stats = {"wins": 0, "loss": 0, "total": 0, "active": True}
selected_pair = None 

def get_tz_now():
    # Inarekebisha muda wa Cloud (UTC) kuwa wa Tanzania (UTC+3)
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)

def send_jabir_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {"chat_id": CHAT_ID, "photo": photo_url, "caption": caption, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=25, verify=False)
    except: pass

def send_jabir_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=15, verify=False)
    except: pass

def get_hq_market_data(symbol):
    try:
        clean_symbol = symbol.replace("-OTC", "")
        ticker = f"{clean_symbol}=X" if clean_symbol not in ["BTCUSD", "XAUUSD"] else (f"BTC-USD" if clean_symbol == "BTCUSD" else "GC=F")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=30m"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=15, verify=False).json()
        c = [x for x in r['chart']['result'][0]['indicators']['quote'][0]['close'] if x is not None]
        if len(c) >= 15:
            mom = c[-1] - c[-6]
            avg_v = sum([abs(c[i]-c[i-1]) for i in range(-10,0)])/10
            if abs(mom) > (avg_v * 2.2): # Strict HQ Filter
                if mom > 0: return "PUT (SELL) 🔴", c[-1]
                if mom < 0: return "CALL (BUY) 🟢", c[-1]
    except: pass
    return None, None

def check_result(symbol, entry_price, action):
    time.sleep(305) 
    _, exit_price = get_hq_market_data(symbol)
    if exit_price:
        win = (("BUY" in action and exit_price > entry_price) or ("SELL" in action and exit_price < entry_price))
        if win:
            session_stats["wins"] += 1
            send_jabir_msg(f"✅ **RESULT: {symbol}**\n🏆 **WIN!**")
        else:
            session_stats["loss"] += 1
            send_jabir_msg(f"❌ **RESULT: {symbol}**\n💀 **LOSS.**")
        
        session_stats["total"] += 1
        if session_stats["wins"] >= SESSION_TARGET:
            send_jabir_msg(f"🏁 **TARGET REACHED!**\n🛑 Jabir, session imefungwa.")
            session_stats["active"] = False

def run_bot():
    print("🔱 JABIR V5400 IS LIVE ON CLOUD 🔱")
    send_jabir_photo(PHOTO_STARTUP, "🔱 **JABIR V5400: MOBILE CLOUD ACTIVE** 🔱\n━━━━━━━━━━━━━━━\n📡 Mode: `24/7 Unlimited` ✅\n🚀 King Jabir, tuko hewani!")
    
    last_signal_time, last_alert_time, current_session_id = "", "", ""
    
    while True:
        try:
            now_dt = get_tz_now()
            now_str = now_dt.strftime("%H:%M")
            
            # Logic ya Session
            active_session = None
            for s in SESSIONS:
                if s["start"] > s["end"]: 
                    if now_str >= s["start"] or now_str < s["end"]: active_session = s; break
                else:
                    if s["start"] <= now_str < s["end"]: active_session = s; break
            
            if active_session and current_session_id != active_session["name"]:
                session_stats.update({"wins": 0, "loss": 0, "total": 0, "active": True})
                caption = (f"📈 **START OF {active_session['name']}**\n━━━━━━━━━━━━━━━\n🚀 Jabir, piga msumari!")
                send_jabir_photo(active_session["photo"], caption)
                current_session_id = active_session["name"]

            if active_session and session_stats["active"]:
                current_pairs = SPECIAL_PAIR_S4 if active_session["name"] == "4TH JABIR SESSION" else NORMAL_PAIRS
                
                # PRE-SIGNAL (Sekunde 50 kabla)
                if now_dt.minute % 5 == 4 and now_dt.second == 10:
                    if last_alert_time != now_str:
                        for symbol in current_pairs:
                            action, _ = get_hq_market_data(symbol)
                            if action:
                                global selected_pair
                                selected_pair = symbol 
                                send_jabir_msg(f"🚨 **PRE-SIGNAL ALERT (50s)** 🚨\n━━━━━━━━━━━━━━━\n🎯 Pair: `{symbol}`\n📢 Jabir, fungua Broker ukae tayari!")
                                last_alert_time = now_str; break

                # MAIN HQ SIGNAL
                if now_dt.minute % 5 == 0 and now_dt.second == 5:
                    if last_signal_time != now_str and selected_pair:
                        action, entry = get_hq_market_data(selected_pair)
                        if action:
                            send_jabir_msg(f"💎 **ELITE HQ SIGNAL**\n━━━━━━━━━━━━━━━\n💰 **PAIR:** `{selected_pair}`\n🚀 **ACTION:** `{action}`\n🎯 **PIGA SASA JABIR!**")
                            last_signal_time = now_str
                            threading.Thread(target=check_result, args=(selected_pair, entry, action)).start()
                        selected_pair = None 
            time.sleep(1)
        except Exception as e:
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
