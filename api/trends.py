"""
TrendPulse API - /api/trends
Fetches real data from Reddit (PRAW) and X/Twitter trends (scraping trends24.in)
Returns momentum scores 0-100 for each ticker
"""

import os
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict
from http.server import BaseHTTPRequestHandler

import praw
import requests
from bs4 import BeautifulSoup


# ============================================================================
# Config
# ============================================================================

REDDIT_SUBREDDITS = ['wallstreetbets', 'cryptocurrency']
POSTS_PER_SUB = 50  # hot + rising combined

# Ticker regex
TICKER_PATTERN = re.compile(r'\$([A-Z]{1,5})\b')
TICKER_MENTION = re.compile(r'\b([A-Z]{2,5})\b')

# Known tickers (validates uppercase words)
KNOWN_TICKERS = {
    # Stocks
    'NVDA', 'TSLA', 'AMD', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    'GME', 'AMC', 'PLTR', 'SOFI', 'HOOD', 'COIN', 'MSTR', 'SPY', 'QQQ',
    'SMCI', 'ARM', 'AVGO', 'MU', 'INTC', 'BA', 'DIS', 'NFLX', 'PYPL',
    # Crypto
    'BTC', 'ETH', 'SOL', 'DOGE', 'XRP', 'ADA', 'DOT', 'AVAX', 'MATIC',
    'LINK', 'SHIB', 'PEPE', 'BONK', 'WIF', 'ARB', 'OP', 'SUI', 'APT',
}

# Sentiment keywords
BULLISH = {'moon', 'pump', 'bullish', 'buy', 'calls', 'long', 'squeeze', 'rocket', 'tendies', 'diamond', '🚀', '📈', '💎'}
BEARISH = {'dump', 'crash', 'bearish', 'sell', 'puts', 'short', 'rekt', 'rug', '📉', '💀', '🐻'}


# ============================================================================
# Reddit Scraper (PRAW)
# ============================================================================

def get_reddit_client():
    """Initialize PRAW Reddit client."""
    return praw.Reddit(
        client_id=os.environ.get('REDDIT_CLIENT_ID'),
        client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
        username=os.environ.get('REDDIT_USERNAME'),
        password=os.environ.get('REDDIT_PASSWORD'),
        user_agent='TrendPulse/1.0'
    )


def extract_tickers(text: str) -> list:
    """Extract valid tickers from text."""
    tickers = set()
    
    # $TICKER format
    for match in TICKER_PATTERN.findall(text):
        if match in KNOWN_TICKERS:
            tickers.add(match)
    
    # Uppercase words (validate against known)
    for match in TICKER_MENTION.findall(text):
        if match in KNOWN_TICKERS:
            tickers.add(match)
    
    return list(tickers)


def calc_sentiment(text: str) -> float:
    """Calculate sentiment score -1 to 1."""
    text_lower = text.lower()
    bull = sum(1 for w in BULLISH if w in text_lower)
    bear = sum(1 for w in BEARISH if w in text_lower)
    total = bull + bear
    if total == 0:
        return 0.0
    return round((bull - bear) / total, 2)


def fetch_reddit_data() -> dict:
    """Fetch posts from Reddit and aggregate by ticker."""
    try:
        reddit = get_reddit_client()
        ticker_data = defaultdict(lambda: {'mentions': 0, 'sentiment_sum': 0, 'scores': [], 'posts': 0, 'subreddit': ''})
        
        for sub_name in REDDIT_SUBREDDITS:
            subreddit = reddit.subreddit(sub_name)
            
            # Fetch hot + rising posts
            posts = list(subreddit.hot(limit=POSTS_PER_SUB // 2)) + list(subreddit.rising(limit=POSTS_PER_SUB // 2))
            
            for post in posts:
                text = f"{post.title} {post.selftext or ''}"
                tickers = extract_tickers(text)
                sentiment = calc_sentiment(text)
                
                for ticker in tickers:
                    ticker_data[ticker]['mentions'] += 1
                    ticker_data[ticker]['sentiment_sum'] += sentiment
                    ticker_data[ticker]['scores'].append(post.score)
                    ticker_data[ticker]['posts'] += 1
                    ticker_data[ticker]['subreddit'] = sub_name
        
        return dict(ticker_data)
    
    except Exception as e:
        print(f"Reddit error: {e}")
        return {}


# ============================================================================
# X/Twitter Trends Scraper (via trends24.in - no auth needed)
# ============================================================================

def fetch_twitter_trends() -> list:
    """Scrape trending topics from trends24.in (mirrors Twitter trends)."""
    try:
        # US trends
        url = "https://trends24.in/united-states/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        trends = []
        
        # Find trend list items
        trend_cards = soup.select('.trend-card__list li a')
        
        for item in trend_cards[:30]:  # Top 30 trends
            text = item.get_text(strip=True)
            if text:
                # Check if it contains a ticker
                tickers = extract_tickers(text.upper())
                if tickers:
                    for ticker in tickers:
                        trends.append({
                            'ticker': ticker,
                            'trend_text': text,
                            'source': 'twitter'
                        })
                # Also check for crypto/stock keywords
                elif any(kw in text.lower() for kw in ['stock', 'crypto', 'bitcoin', 'ethereum', '$']):
                    trends.append({
                        'ticker': text[:10],
                        'trend_text': text,
                        'source': 'twitter'
                    })
        
        return trends
    
    except Exception as e:
        print(f"Twitter trends error: {e}")
        return []


# ============================================================================
# Momentum Calculation
# ============================================================================

def calc_momentum(mentions: int, avg_score: float, sentiment: float) -> int:
    """
    Calculate momentum score 0-100.
    
    Factors:
    - Mention volume (log scaled, 40%)
    - Avg post score (log scaled, 30%)
    - Sentiment strength (30%)
    """
    import math
    
    # Mention score (0-40)
    mention_score = min(40, math.log10(max(1, mentions)) * 20)
    
    # Score score (0-30)
    score_score = min(30, math.log10(max(1, avg_score)) * 10)
    
    # Sentiment score (0-30)
    sentiment_score = (abs(sentiment) + 0.5) * 20  # Boost for strong sentiment
    sentiment_score = min(30, sentiment_score)
    
    momentum = int(mention_score + score_score + sentiment_score)
    return max(0, min(100, momentum))


# ============================================================================
# Main Handler
# ============================================================================

def build_response():
    """Build the trends response combining Reddit and Twitter data."""
    trends = []
    
    # Reddit data
    reddit_data = fetch_reddit_data()
    for ticker, data in reddit_data.items():
        avg_sentiment = data['sentiment_sum'] / max(1, data['mentions'])
        avg_score = sum(data['scores']) / max(1, len(data['scores']))
        momentum = calc_momentum(data['mentions'], avg_score, avg_sentiment)
        
        trends.append({
            'ticker': f"${ticker}",
            'source': 'reddit',
            'momentum': momentum,
            'mentions': data['mentions'],
            'sentiment': round(avg_sentiment, 2),
            'subreddit': data['subreddit'],
            'posts': data['posts']
        })
    
    # Twitter trends
    twitter_data = fetch_twitter_trends()
    twitter_tickers = defaultdict(int)
    for t in twitter_data:
        twitter_tickers[t['ticker']] += 1
    
    for ticker, count in twitter_tickers.items():
        # Twitter trends get moderate momentum (we don't have sentiment)
        momentum = min(80, 30 + count * 10)
        
        # Check if also on Reddit (boost)
        if ticker.replace('$', '') in reddit_data:
            momentum = min(95, momentum + 15)
        
        trends.append({
            'ticker': f"${ticker}" if not ticker.startswith('$') else ticker,
            'source': 'twitter',
            'momentum': momentum,
            'mentions': count,
            'sentiment': 0.1,  # Neutral-positive assumption for trending
            'subreddit': None,
            'posts': 0
        })
    
    # Sort by momentum
    trends.sort(key=lambda x: x['momentum'], reverse=True)
    
    # Dedupe by ticker (keep highest momentum)
    seen = set()
    unique_trends = []
    for t in trends:
        ticker = t['ticker'].upper()
        if ticker not in seen:
            seen.add(ticker)
            unique_trends.append(t)
    
    return {
        'trends': unique_trends[:20],  # Top 20
        'updated': datetime.utcnow().isoformat(),
        'sources': {
            'reddit': len(reddit_data),
            'twitter': len(twitter_tickers)
        }
    }


# Vercel serverless handler
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = build_response()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'max-age=60')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()
