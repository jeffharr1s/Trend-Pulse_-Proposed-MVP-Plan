"""
TrendPulse - X/Twitter Selenium Scraper (LOCAL ONLY)
====================================================
Scrapes x.com/explore trends using headless Chrome.
Run locally, outputs JSON that can be used by the API.

Usage:
    python scripts/scrape_x.py > x_trends.json

Requirements:
    pip install selenium webdriver-manager

Note: This runs LOCALLY only. Vercel uses trends24.in fallback.
"""

import json
import re
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Known tickers for validation
KNOWN_TICKERS = {
    'NVDA', 'TSLA', 'AMD', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    'GME', 'AMC', 'PLTR', 'SOFI', 'HOOD', 'COIN', 'MSTR', 'SPY', 'QQQ',
    'SMCI', 'ARM', 'AVGO', 'MU', 'INTC', 'BA', 'DIS', 'NFLX', 'PYPL',
    'BTC', 'ETH', 'SOL', 'DOGE', 'XRP', 'ADA', 'DOT', 'AVAX', 'MATIC',
    'LINK', 'SHIB', 'PEPE', 'BONK', 'WIF', 'ARB', 'OP', 'SUI', 'APT',
}

TICKER_PATTERN = re.compile(r'\$([A-Z]{1,5})\b')


def create_driver():
    """Create headless Chrome driver."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scrape_x_explore():
    """Scrape x.com/explore for trending topics."""
    driver = None
    trends = []
    
    try:
        driver = create_driver()
        
        # Go to explore page (no login required for trends)
        driver.get('https://x.com/explore/tabs/trending')
        
        # Wait for trends to load
        time.sleep(5)  # Allow JS to render
        
        # Try to find trend elements
        # X uses various selectors, try multiple
        selectors = [
            '[data-testid="trend"]',
            '[data-testid="cellInnerDiv"]',
            'div[aria-label*="Trending"]',
            'section[aria-labelledby*="accessible"] div span'
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    break
            except:
                continue
        
        # Extract text from trend elements
        seen = set()
        for elem in elements[:50]:
            try:
                text = elem.text.strip()
                if not text or text in seen:
                    continue
                seen.add(text)
                
                # Look for tickers
                for match in TICKER_PATTERN.findall(text.upper()):
                    if match in KNOWN_TICKERS:
                        trends.append({
                            'ticker': f'${match}',
                            'text': text[:100],
                            'source': 'twitter'
                        })
                
                # Check for crypto/stock keywords
                keywords = ['bitcoin', 'ethereum', 'crypto', 'stock', 'trading', 'btc', 'eth']
                if any(kw in text.lower() for kw in keywords):
                    trends.append({
                        'ticker': text.split()[0][:10],
                        'text': text[:100],
                        'source': 'twitter'
                    })
                    
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"Error: {e}", file=__import__('sys').stderr)
    
    finally:
        if driver:
            driver.quit()
    
    return trends


def main():
    """Main entry point."""
    print(f"Scraping X trends at {datetime.utcnow().isoformat()}...", file=__import__('sys').stderr)
    
    trends = scrape_x_explore()
    
    output = {
        'trends': trends,
        'count': len(trends),
        'scraped_at': datetime.utcnow().isoformat(),
        'source': 'x.com/explore'
    }
    
    # Output JSON to stdout
    print(json.dumps(output, indent=2))
    
    print(f"Found {len(trends)} trends", file=__import__('sys').stderr)


if __name__ == '__main__':
    main()
