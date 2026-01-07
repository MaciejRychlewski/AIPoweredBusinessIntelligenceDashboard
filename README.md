# AI-Powered Market & News Briefing App

A personal intelligence assistant that gathers business news, analyzes articles with AI, and delivers a prioritized briefing — plus optional market data snapshots.

Built to eliminate information overload and surface only what matters.

---

## Features

### AI-Powered News Summaries
- Scrapes BBC Business/Tech/Politics/Science headlines
- Extracts full article content
- Uses Google's Gemini model to:
  - summarize each article
  - rate relevance (0–5)
  - explain why the score was given
- Filters out low-value content

### Live Market Data (Optional)
Fetches real-time prices from **Yahoo Finance**:
- Stocks (S&P 500, NASDAQ, DAX…)
- Crypto (BTC, ETH, DOGE)
- Forex (USD/PLN, EUR/PLN…)
- Commodities (Oil, Gold, Silver)
- Bonds (US Treasuries)

Rendered as a clean HTML table.

### Email Your Briefing
Send your final report directly to your inbox:
- formatted HTML
- ready to save, forward, or print

### Clean UI
Built with **Gradio**
- input form
- loading animation
- final report view
- email action

---

## Tech Stack

**Python**
- BeautifulSoup + Selenium (scraping)
- Trafilatura (article extraction)
- Gemini (AI summaries & scoring)
- yfinance (market data)
- python-dotenv (environment secrets)
- Gradio (UI)
- smtplib + MIME (email sending)

---

## Project Structure

├── app.py                  # Main UI + report orchestration
├── briefing_module.py      # Scrapes + AI scoring of news articles
├── market_module.py        # Live market data retrieval
├── email_module.py         # HTML email sending
├── requirements.txt        # Dependencies
├── .env.example            # Required environment variables
└── .gitignore              # Excludes secrets/cache files

---

## Setup & Run

- Clone the repository  
  git clone https://github.com/<your-username>/<repo-name>.git  
  cd <repo-name>

- Install dependencies  
  pip install -r requirements.txt

- Create your .env file  
  Duplicate .env.example and rename it to .env, then fill in your values:  
  GOOGLE_API_KEY=your_google_key  
  EMAIL_USER=your_email@gmail.com  
  EMAIL_PASSWORD=your_gmail_app_password  
  EMAIL_TO=recipient@example.com

- Run the application  
  python3 app.py  
  Gradio will open automatically in your browser

## Notes

- Gemini API key required  
- Gmail requires an App Password if you use 2FA  
- Scraping takes a bit of time (Selenium + AI processing)  
- Yahoo Finance may limit fast refreshes
