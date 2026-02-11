# 📊 TrendPulse MVP

Real-time social sentiment tracker for trading signals.

**Phase 1:** Reddit + X trends → Momentum scores → Dashboard

## 🚀 Quick Deploy to Vercel

### 1. Get Reddit API Credentials

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click **"create another app..."**
3. Select **"script"** type
4. Fill in name: `TrendPulse`, redirect: `http://localhost:8080`
5. Note your `client_id` (under app name) and `secret`

### 2. Deploy to Vercel

```bash
# Clone/download this repo
cd trendpulse-mvp

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow prompts, then add environment variables:
vercel env add REDDIT_CLIENT_ID
vercel env add REDDIT_CLIENT_SECRET
vercel env add REDDIT_USERNAME
vercel env add REDDIT_PASSWORD

# Redeploy with env vars
vercel --prod
```

**Or via Vercel Dashboard:**
1. Push to GitHub
2. Import at [vercel.com/new](https://vercel.com/new)
3. Add env vars in Project Settings > Environment Variables
4. Deploy

### 3. Done!

Visit your `.vercel.app` URL. Dashboard auto-refreshes every 60s.

---

## 📁 Project Structure

```
trendpulse-mvp/
├── src/
│   ├── App.jsx          # Dashboard (single component)
│   └── main.jsx         # Entry point
├── api/
│   └── trends.py        # Serverless: Reddit + X scraping
├── scripts/
│   └── scrape_x.py      # Local Selenium X scraper (optional)
├── vercel.json          # Vercel config
├── package.json
├── requirements.txt     # Python deps for API
└── .env.example
```

## 🔧 Local Development

```bash
# Frontend
npm install
npm run dev

# API (separate terminal) - need to run Python locally
pip install praw requests beautifulsoup4
python -m http.server 3001  # Or use vercel dev
```

## 📊 How It Works

### Data Sources
- **Reddit:** PRAW API → r/wallstreetbets, r/cryptocurrency (hot + rising)
- **X/Twitter:** Scrapes trends24.in (no auth needed, mirrors Twitter trends)

### Momentum Score (0-100)
```
momentum = mention_volume(40%) + post_scores(30%) + sentiment(30%)
```

### Signals
| Momentum | Sentiment | Signal |
|----------|-----------|--------|
| ≥70      | >0.2      | BUY    |
| ≤30      | <-0.3     | SELL   |
| ≥50      | >0        | WATCH  |
| other    | other     | HOLD   |

## 🛠️ Optional: Local X Selenium Scraper

For real x.com scraping (runs locally only):

```bash
pip install selenium webdriver-manager
python scripts/scrape_x.py > x_trends.json
```

Note: Vercel can't run Selenium, so deployed version uses trends24.in fallback.

---

## 📋 Roadmap

- [x] **Phase 1:** Reddit + X trends, momentum scores, dashboard
- [ ] **Phase 2:** Discord webhook alerts, email notifications
- [ ] **Phase 3:** Alpaca/Coinbase quick trade execution

---

## ⚠️ Disclaimer

Not financial advice. Use at your own risk. Paper trade first.
