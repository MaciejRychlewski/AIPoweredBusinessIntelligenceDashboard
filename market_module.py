import yfinance as yf


def get_market_data(selected_categories):
    """
    Fetch selected market data categories using Yahoo Finance
    and return preformatted HTML table rows.

    Args:
        selected_categories (list[str]): List of category names
            matching keys in the `all_tickers` dictionary.

    Returns:
        str: HTML snippet with table rows for each market instrument,
             or a message if no categories were selected.
    """
    print(f"📈 Fetching Market Data for: {selected_categories}...")

    all_tickers = {
        "Stocks": {
            "🇺🇸 S&P 500": "^GSPC",
            "🇺🇸 NASDAQ": "^IXIC",
            "🇩🇪 DAX": "^GDAXI",
            "🇯🇵 Nikkei": "^N225",
        },
        "Crypto": {
            "₿ Bitcoin": "BTC-USD",
            "Ξ Ethereum": "ETH-USD",
            "Dogecoin": "DOGE-USD",
        },
        "Forex": {
            "💵 USD/PLN": "PLN=X",
            "💶 EUR/PLN": "EURPLN=X",
            "💷 GBP/USD": "GBPUSD=X",
        },
        "Commodities": {
            "🛢️ Oil (WTI)": "CL=F",
            "🥇 Gold": "GC=F",
            "🥈 Silver": "SI=F",
        },
        "Bonds": {
            "🇺🇸 10Y Treasury": "^TNX",
            "🇺🇸 5Y Treasury": "^FVX",
            "🇺🇸 13 Week Bill": "^IRX",
        },
    }

    rows_html = ""

    if not selected_categories:
        return "<p>No market data selected.</p>"

    for category in selected_categories:
        if category in all_tickers:
            # Header row for the category
            rows_html += (
                f"<tr><td colspan='3' style='background:#f1f5f9;"
                f"font-weight:800;padding:10px;font-size:12px;"
                f"letter-spacing:1px;color:#475569;'>"
                f"{category.upper()}</td></tr>"
            )

            for name, symbol in all_tickers[category].items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="5d")

                    if len(data) >= 1:
                        price = data["Close"].iloc[-1]
                        change_html = "-"

                        if len(data) >= 2:
                            prev = data["Close"].iloc[-2]
                            change = ((price - prev) / prev) * 100
                            color = "#10b981" if change >= 0 else "#ef4444"
                            sign = "+" if change >= 0 else ""
                            change_html = (
                                f'<span style="color: {color}; font-weight: bold;">'
                                f'{sign}{change:.2f}%</span>'
                            )

                        rows_html += f"""
                        <tr>
                            <td style="padding: 10px; border-bottom:1px solid #e2e8f0;">{name}</td>
                            <td style="padding: 10px; text-align: right; font-family:monospace; border-bottom:1px solid #e2e8f0;">{price:,.2f}</td>
                            <td style="padding: 10px; text-align: right; font-family:monospace; border-bottom:1px solid #e2e8f0;">{change_html}</td>
                        </tr>
                        """
                except Exception:
                    # Skip tickers that fail to fetch
                    continue

    return rows_html