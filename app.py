import os
import time

import gradio as gr
from dotenv import load_dotenv

import briefing_module
import market_module
import email_module

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEFAULT_RECIPIENT = os.getenv("EMAIL_TO")

ai_model = briefing_module.configure_ai(API_KEY)

custom_css = """
<style>
    body { background-color: #f8fafc; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    /* LOADER */
    .loader-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 400px; text-align: center; background: white; border-radius: 24px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
    }
    .pulse-ring {
        width: 60px; height: 60px; background: #3b82f6; border-radius: 50%;
        animation: pulse 2s infinite; margin-bottom: 30px;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(59, 130, 246, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
    }
    .loading-title { font-size: 26px; font-weight: 700; color: #1e293b; margin-bottom: 10px;}
    .loading-desc { font-size: 16px; color: #64748b; max-width: 400px; line-height: 1.5; }

    /* REPORT */
    .glass-card {
        background: white; border-radius: 16px; padding: 30px; margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border: 1px solid #f1f5f9;
    }
    .badge { padding: 4px 10px; border-radius: 6px; color: white; font-weight: bold; font-size: 11px; text-transform: uppercase; }
    a { color: #2563eb; text-decoration: none; font-weight: 600; }
</style>
"""

STATIC_LOADER_HTML = """
<div class="loader-container">
    <div class="pulse-ring"></div>
    <div class="loading-title">AI Agent is Researching...</div>
    <div class="loading-desc">
        Deep scanning global sources & analyzing market data. Please wait while we curate your intelligence report.
        <br><br><span style="font-size:12px; opacity:0.7;">Est. time: ~2 minutes (Deep Search)</span>
    </div>
</div>
"""


def generate_report_logic(category, market_options, user_topic):
    """
    Gradio callback to generate the intelligence report.

    Steps:
      - hide input view, show loading view
      - optionally fetch and render market data
      - scrape news headlines and analyze them with the AI model
      - build final HTML report with summaries and relevance scores
    """
    # Switch views: hide input, show loading, hide output
    yield (
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
        "",
    )

    market_html = ""
    if market_options:
        try:
            market_rows = market_module.get_market_data(market_options)
            market_html = (
                "<div class='glass-card'>"
                "<h2>📉 Market Snapshot</h2>"
                "<table style='width:100%; border-collapse:collapse;'>"
                f"{market_rows}</table></div>"
            )
        except Exception:
            market_html = "<div class='glass-card'>Market Data Unavailable</div>"

    try:
        driver = briefing_module.setup_driver()
        headlines = briefing_module.fetch_headlines(
            driver, category=category, limit=12
        )
        driver.quit()
    except Exception as e:
        # Connection or scraping error
        yield (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            f"Connection Error: {e}",
        )
        return

    scored_articles = []
    for item in headlines:
        try:
            result = briefing_module.analyze_article_with_score(
                ai_model, item["link"], user_topic
            )

            # Avoid hammering the API
            time.sleep(3)

            if result and result.get("score", 0) >= 2:
                result["link"] = item["link"]
                scored_articles.append(result)
        except Exception:
            continue

    scored_articles.sort(key=lambda x: x["score"], reverse=True)

    final_report = custom_css + market_html
    final_report += (
        "<div class=\"glass-card\">"
        f"<h2>📰 Intelligence Briefing: {category}</h2>"
        f"<p style='color:#64748b;'>Focus: {user_topic}</p>"
    )

    if not scored_articles:
        final_report += (
            "<p>No highly relevant news found "
            "(AI filtered out low relevance articles).</p>"
        )

    for article in scored_articles:
        score = article["score"]
        bg_color = (
            "#10b981"
            if score == 5
            else ("#f59e0b" if score >= 3 else "#94a3b8")
        )

        final_report += f"""
        <div style="margin-bottom: 25px; border-bottom: 1px solid #f1f5f9; padding-bottom: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <h3 style="margin:0; font-size:18px; color:#1e293b;">{article['title']}</h3>
                <span class="badge" style="background: {bg_color};">{score}/5</span>
            </div>
            <div style="margin-top:10px; line-height:1.6; color:#334155; font-size:15px;">{article['summary']}</div>
            <div style="margin-top:10px;">
                <a href="{article['link']}" target="_blank">Read Full Source ›</a>
            </div>
        </div>
        """

    final_report += "</div>"

    # Final view: show output, hide input and loader
    yield (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        final_report,
    )


def send_email_logic(html_content, recipient):
    """
    Gradio callback for the "Send to Email" button.

    Validates that there is generated content and delegates sending
    to the email_module.
    """
    if not html_content or len(html_content) < 50:
        return "⚠️ Generate a report first!"

    status = email_module.send_email(
        EMAIL_USER, EMAIL_PASSWORD, recipient, html_content
    )
    return status


def reset_app():
    """
    Reset the UI back to the initial state:
    - show input view
    - hide loading and output views
    - clear the report display
    """
    return (
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        "",
    )


with gr.Blocks(
    css=custom_css,
    title="Business Intelligence Dashboard",
) as app:
    with gr.Column(visible=True) as input_view:
        gr.Markdown("# 💎 Business Intelligence Dashboard", elem_classes="text-center")

        with gr.Row():
            with gr.Column(scale=1):
                category_dropdown = gr.Dropdown(
                    label="Source Channel",
                    choices=["Business", "Technology", "Politics", "Science"],
                    value="Business",
                )
                market_checkbox = gr.CheckboxGroup(
                    label="Market Data",
                    choices=[
                        "Stocks",
                        "Crypto",
                        "Forex",
                        "Commodities",
                        "Bonds",
                    ],
                    value=["Stocks", "Crypto", "Bonds"],
                )

            with gr.Column(scale=2):
                topic_input = gr.Textbox(
                    label="Focus Topic",
                    placeholder="e.g. Artificial Intelligence...",
                )
                gr.Examples(
                    [
                        "Artificial Intelligence",
                        "Recession",
                        "Startups",
                        "Global Politics",
                    ],
                    inputs=topic_input,
                )

        generate_btn = gr.Button(
            "🚀 Generate Report",
            variant="primary",
            size="lg",
        )

    with gr.Column(visible=False) as loading_view:
        gr.HTML(value=STATIC_LOADER_HTML)

    with gr.Column(visible=False) as output_view:
        with gr.Row():
            gr.Markdown("## 📑 Intelligence Report")
            back_btn = gr.Button(
                "🔄 New Search",
                size="sm",
                variant="secondary",
            )

        report_display = gr.HTML()

        gr.Markdown("---")
        with gr.Row(variant="panel"):
            with gr.Column(scale=3):
                email_input = gr.Textbox(
                    label="Recipient Email",
                    value=DEFAULT_RECIPIENT,
                    placeholder="name@example.com",
                )
            with gr.Column(scale=1):
                email_btn = gr.Button(
                    "📩 Send to Email",
                    variant="primary",
                )

        email_status = gr.Textbox(
            label="Status",
            interactive=False,
            visible=True,
        )

    generate_btn.click(
        fn=generate_report_logic,
        inputs=[category_dropdown, market_checkbox, topic_input],
        outputs=[input_view, loading_view, output_view, report_display],
        show_progress="hidden",
    )

    back_btn.click(
        fn=reset_app,
        outputs=[input_view, loading_view, output_view, report_display],
    )

    email_btn.click(
        fn=send_email_logic,
        inputs=[report_display, email_input],
        outputs=[email_status],
    )

if __name__ == "__main__":
    app.launch()