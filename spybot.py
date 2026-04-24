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
    # 1. Fetch Monthly Data
    # '3mo' gives us enough history to identify the previous full month's range
    df = yf.download(TICKER, period="3mo", interval="1mo")
    
    if len(df) < 2:
        print("Error: Not enough historical data.")
        return

    # 2. Identify Strategy Levels (Previous Month)
    # iloc[-2] is the most recently completed month
    prev_month = df.iloc[-2]
    prev_high = prev_month['High']
    prev_low = prev_month['Low']

    # 3. Get Real-Time Price
    ticker_obj = yf.Ticker(TICKER)
    # Using fast_info for efficient price fetching
    current_price = ticker_obj.fast_info['last_price']

    # 4. Signal Logic
    header = f"🔔 *{TICKER} Swing Alert*"
    status = f"Current Price: `${current_price:.2f}`"
    levels = f"📉 Buy Target (LL): `${prev_low:.2f}`\n📈 Sell Target (High): `${prev_high:.2f}`"
    
    signal_msg = ""

    # Check for Buy Signal (Lower Low Entry)
    if current_price <= prev_low:
        signal_msg = f"{header}\n\n{status}\n{levels}\n\n🚀 **SIGNAL: BUY ENTRY.**\nPrice is at or below the monthly lower low. Potential reversal zone."
    
    # Check for Sell Signal (Monthly High Exit)
    elif current_price >= prev_high:
        signal_msg = f"{header}\n\n{status}\n{levels}\n\n💰 **SIGNAL: TAKE PROFIT.**\nPrice has reached the monthly high target."
    
    # Optional: Periodic update even if no signal is hit
    else:
        print(f"No signal. Current: {current_price:.2f} | Range: {prev_low:.2f} - {prev_high:.2f}")
        # Uncomment the line below if you want a daily status update regardless of signals
        # signal_msg = f"{header} (No Action Required)\n\n{status}\n{levels}"

    if signal_msg:
        send_telegram_msg(signal_msg)
        print("Signal sent to Telegram.")

if __name__ == "__main__":
    run_swing_strategy()
