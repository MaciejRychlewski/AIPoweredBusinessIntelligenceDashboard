import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import trafilatura
import time
import json
import os


def configure_ai(api_key):
    """
    Configure the Gemini model using the given API key.

    Uses 'gemini-flash-latest' as the model.
    Returns a GenerativeModel instance or None if configuration fails.
    """
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-flash-latest")
    except Exception as e:
        print(f"⚠️ AI Config Error: {e}")
        return None


def setup_driver():
    """
    Launch a headless Chrome browser with basic performance settings.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def fetch_headlines(driver, category="Business", limit=6):
    """
    Scrape BBC headlines for a given category.

    Args:
        driver: Selenium WebDriver instance.
        category: One of the predefined BBC news sections.
        limit: Maximum number of articles to return.

    Returns:
        A list of dicts with keys: 'title', 'link'.
    """
    urls = {
        "Business": "https://www.bbc.com/news/business",
        "Technology": "https://www.bbc.com/news/technology",
        "Politics": "https://www.bbc.com/news/politics",
        "Science": "https://www.bbc.com/news/science_and_environment",
        "Health": "https://www.bbc.com/news/health",
    }

    target_url = urls.get(category, urls["Business"])

    print(f"🌐 Scanning BBC Section: {category} ({target_url})...")
    driver.get(target_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    links_found = []

    elements = soup.find_all(["h2", "h3"])

    for element in elements:
        link_tag = element.find("a")
        if not link_tag:
            link_tag = element.find_parent("a")

        if link_tag:
            href = link_tag.get("href", "")
            title = element.get_text(strip=True)

            if href and len(title) > 15:
                if not href.startswith("http"):
                    href = "https://www.bbc.com" + href
                if href not in [x["link"] for x in links_found]:
                    links_found.append({"title": title, "link": href})

    print(f"🔍 Found raw articles in {category}. Selecting top {limit}...")
    return links_found[:limit]


def analyze_article_with_score(model, url, user_topic):
    """
    Download an article, extract text, and analyze it with Gemini.

    The model returns a JSON object with:
      - title: concise title
      - summary: 80–100 word professional summary (EN)
      - score: integer 0–5 (relevance to user_topic)
      - reason: short explanation of the score

    Returns:
        Parsed JSON (dict) or None if analysis fails.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        clean_text = trafilatura.extract(downloaded)
    except Exception:
        return None

    if not clean_text or len(clean_text) < 200:
        return None

    prompt = f"""
    You are an expert AI News Assistant.
    The user is interested in: "{user_topic}".

    Analyze the article below.

    Output MUST be a valid JSON object with these fields:
    - title: (string) A concise title.
    - summary: (string) A professional summary (80-100 words) in ENGLISH.
    - score: (integer) Relevance score from 0 to 5 (5 = critical for {user_topic}, 0 = irrelevant).
    - reason: (string) Brief explanation for the score.

    Article content:
    {clean_text[:15000]}
    """

    for attempt in range(3):
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            return json.loads(response.text)

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"⏳ Quota limit hit. Waiting 20s... (Attempt {attempt + 1})")
                time.sleep(20)
            else:
                print(f"⚠️ AI Error: {e}")
                return None

    return None
