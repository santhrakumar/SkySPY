import yfinance as yf
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load variables from .env file (for local testing)
load_dotenv()

# --- CONFIGURATION ---
TICKER = "SPY"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_msg(message):
    """Sends a formatted alert to the Telegram bot."""
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: BOT_TOKEN or CHAT_ID not found in environment.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Telegram Error: {e}")

def run_swing_strategy():
    print(f"Starting {TICKER} Swing Analysis...")
    
    # 1. Fetch Monthly Data
    # We fetch 3 months to ensure we have the full 'Previous' month data
    df = yf.download(TICKER, period="3mo", interval="1mo")
    
    if df.empty or len(df) < 2:
        print("Error: Could not retrieve enough historical data.")
        return

    # 2. Identify Strategy Levels (Previous Month)
    # The fix: Ensure we extract a single float even if yfinance returns a MultiIndex Series
    try:
        # iloc[-2] is the most recently completed month
        prev_month_data = df.iloc[-2]
        
        # Handle cases where columns might be (Price, Ticker)
        if isinstance(prev_month_data['High'], pd.Series):
            prev_high = float(prev_month_data['High'][TICKER])
            prev_low = float(prev_month_data['Low'][TICKER])
        else:
            prev_high = float(prev_month_data['High'])
            prev_low = float(prev_month_data['Low'])
            
    except Exception as e:
        print(f"Data Extraction Error: {e}")
        return

    # 3. Get Real-Time Price
    try:
        ticker_obj = yf.Ticker(TICKER)
        current_price = float(ticker_obj.fast_info['last_price'])
    except Exception as e:
        print(f"Real-time Price Error: {e}")
        return

    # 4. Signal Logic
    header = f"🔔 *{TICKER} Monthly Swing Alert*"
    status = f"Current Price: `${current_price:.2f}`"
    levels = f"📉 Buy Target (Prev Low): `${prev_low:.2f}`\n📈 Sell Target (Prev High): `${prev_high:.2f}`"
    
    signal_msg = ""

    # Check for Buy Signal (Lower Low / Touch Monthly Low)
    if current_price <= prev_low:
        signal_msg = (f"{header}\n\n{status}\n{levels}\n\n"
                     f"🚀 **SIGNAL: BUY ENTRY.**\n"
                     f"Price is testing the Monthly Lower Low. Satellite position entry zone.")
    
    # Check for Sell Signal (Monthly High Exit)
    elif current_price >= prev_high:
        signal_msg = (f"{header}\n\n{status}\n{levels}\n\n"
                     f"💰 **SIGNAL: TAKE PROFIT.**\n"
                     f"Price has reached the Monthly High. Exit satellite position.")
    
    else:
        print(f"No signal triggered. Price: {current_price:.2f} (Range: {prev_low:.2f} - {prev_high:.2f})")
        # Optional: Uncomment below for daily updates regardless of signals
        # signal_msg = f"{header} (Monitoring)\n\n{status}\n{levels}"

    if signal_msg:
        send_telegram_msg(signal_msg)
        print("Signal sent to Telegram successfully.")

if __name__ == "__main__":
    run_swing_strategy()
