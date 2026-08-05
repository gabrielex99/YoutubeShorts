# `techhacks-growth`: Standalone Growth Agent & Analytics Dashboard

`techhacks-growth` is an autonomous analytics and growth acceleration suite for **TechHacks AI**, dedicated to tracking performance, optimizing affiliate conversions, and scaling traffic across:

- 🔴 **YouTube Shorts**: [`@techhacks_aii`](https://www.youtube.com/@techhacks_aii)
- 📸 **Instagram Reels**: [`@techs_ai1`](https://www.instagram.com/techs_ai1/)
- 🔗 **Beacons Link in Bio**: [`beacons.ai/techhacks.ai`](https://beacons.ai/techhacks.ai)

---

## 📁 Project Architecture

```
techhacks-growth/
├── .env.example                  # Environment blueprint
├── requirements.txt              # Project dependencies
├── main.py                       # Growth CLI & pipeline runner
├── data/
│   └── analytics_history.json    # Time-series metrics storage
├── src/
│   ├── youtube_tracker.py        # YouTube Shorts subscriber & view tracker
│   ├── instagram_tracker.py      # Instagram Reels follower & reach tracker
│   ├── beacons_tracker.py        # Beacons bio link click & CTR tracker
│   ├── growth_radar.py           # Gemini-powered growth recommendation engine
│   └── growth_reporter.py        # Telegram daily growth report dispatcher
└── dashboard/
    ├── index.html                # Web analytics dashboard (dark tech UI)
    ├── style.css                 # Styling system
    └── app.js                    # Interactive charts (Chart.js)
```

---

## 🎮 How to Run

### 1. Run Growth Analytics Sync & Telegram Report
```bash
python3 techhacks-growth/main.py --dry-run
```

### 2. Launch Web Growth Dashboard in Browser
```bash
python3 techhacks-growth/main.py --open-dashboard
```
