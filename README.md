SPY Core-Satellite Swing Bot
An automated trading monitor that tracks the SPDR S&P 500 ETF (SPY). The bot follows a Core-Satellite strategy, identifying tactical swing opportunities when the current price hits monthly extremes.

📈 Strategy Overview
Core: Long-term hold of SPY for stable index growth.

Satellite: Tactical swing trades executed on monthly signals.

Buy Signal: Triggered when the current price hits or drops below the Previous Month’s Low (Lower Low detection).

Sell Signal: Triggered when the price reaches the Previous Month’s High.

🛠️ Tech Stack
Language: Python 3.x

Data Source: yfinance

Communication: Telegram Bot API

Automation: GitHub Actions (Scheduled via Cron)
