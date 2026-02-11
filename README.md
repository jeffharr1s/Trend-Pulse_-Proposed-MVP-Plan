# 📊 TrendPulse MVP

Real-time social sentiment tracker for trading signals.

**Phase 1:** Reddit + X trends → Momentum scores → Dashboard  
**Phase 2:** Discord + Email alerts ✅

## 🚀 Quick Deploy to Vercel

### 1. Get Reddit API Credentials

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click **"create another app..."**
3. Select **"script"** type
4. Fill in name: `TrendPulse`, redirect: `http://localhost:8080`
5. Note your `client_id` (under app name) and `secret`

### 2. Set Up Alerts (Optional)

**Discord Webhook:**
1. Open Discord server → Settings → Integrations → Webhooks
2. Click **New Webhook** → Copy URL

**Resend Email:**
1. Sign up at [resend.com](https://resend.com) (free: 3k/month)
2. Create API key at [resend.com/api-keys](https://resend.com/api-keys)

### 3. Deploy to Vercel

```bash
# Clone/download this repo
cd trendpulse-mvp

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Add environment variables:
vercel env add REDDIT_CLIENT_ID
vercel env add REDDIT_CLIENT_SECRET
vercel env add REDDIT_USERNAME
vercel env add REDDIT_PASSWORD

# Optional: Alerts
vercel env add DISCORD_WEBHOOK_URL
vercel env add RESEND_API_KEY
vercel env add ALERT_EMAIL

# Redeploy with env vars
vercel --prod
```

### 4. Done!

Visit your `.vercel.app` URL. Toggle alerts with 🔔 button.

---

## 📁 Project Structure

```
trendpulse-mvp/
├── src/
│   ├── App.jsx          # Dashboard + alerts UI
│   └── main.jsx         # Entry point
├── api/
│   ├── trends.py        # Reddit + X scraping
│   └── alert.py         # Discord/email alerts
├── scripts/
│   └── scrape_x.py      # Local Selenium X scraper
├── vercel.json
├── package.json
├── requirements.txt
└── .env.example
```

## 🔔 Alert System

### Triggers
| Signal | Condition | Auto-Alert |
|--------|-----------|------------|
| BUY | Momentum ≥70, Sentiment >0.2 | ✅ When enabled |
| SELL | Momentum ≤30 OR Sentiment <-0.3 | ✅ When enabled |
| WATCH | Momentum ≥50 | Manual only |

### Channels
- **Discord:** Rich embed with color-coded signals
- **Email:** Clean HTML email via Resend

### Manual Alerts
Click 🔔 **Send Alert** on any BUY/SELL card.

### Auto Alerts
Toggle 🔔 **Alerts ON** in header. Triggers on:
- BUY signals with momentum ≥75
- Checked every refresh (60s)

---

## 📊 How It Works

### Data Sources
- **Reddit:** PRAW API → r/wallstreetbets, r/cryptocurrency (hot + rising)
- **X/Twitter:** Scrapes trends24.in (mirrors Twitter trends)

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

---

## 🛠️ API Reference

### GET /api/trends
Returns trending tickers with momentum scores.

### POST /api/alert
Send alert for a ticker.
```json
{
  "ticker": "$NVDA",
  "signal": "BUY",
  "momentum": 85,
  "sentiment": 0.45,
  "source": "reddit",
  "channels": ["discord", "email"]
}
```

---

## 📋 Roadmap

- [x] **Phase 1:** Reddit + X trends, momentum scores, dashboard
- [x] **Phase 2:** Discord webhook alerts, email notifications
- [ ] **Phase 3:** Alpaca/Coinbase quick trade execution

---

## ⚠️ Disclaimer

Not financial advice. Use at your own risk. Paper trade first.
