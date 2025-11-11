# 🚀 Altseason Sentinel

> Real-time cryptocurrency market intelligence dashboard for monitoring altseason signals and critical market conditions

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 📊 Overview

Altseason Sentinel is a sophisticated market monitoring system that tracks critical cryptocurrency market conditions in real-time. Built with Python, it provides actionable intelligence through terminal dashboards, Discord notifications, email alerts, and historical data logging.

### Key Features

- **Real-time Market Analysis**: Monitors BTC dominance, altcoin dominance, and stablecoin flows
- **Altseason Probability Score**: Proprietary algorithm calculating optimal entry/exit windows (0-100%)
- **Critical Level Tracking**: Automated alerts for key BTC price levels ($104K, $116K, $88K zones)
- **Old Coin Revival Scanner**: Detects volume anomalies in historical cryptocurrencies
- **Multi-Platform Notifications**: Terminal UI, Discord webhooks, and email alerts
- **Data Logging**: Comprehensive CSV export for backtesting and analysis

## 🎯 Problem Solved

During cryptocurrency market cycles, timing is critical. This tool addresses:

1. **Information Overload**: Synthesizes multiple data sources into actionable signals
2. **Missed Opportunities**: Real-time alerts prevent missing key market transitions
3. **Emotional Trading**: Data-driven probability scores replace gut feelings
4. **Pattern Recognition**: Identifies historical cycle patterns (e.g., "old coin revivals")

## 📈 Live Dashboard Example

```
🚀 ALTSEASON SENTINEL 🚀
Target Date: Dec 15, 2025 (34 days remaining)
Last Update: 2025-11-10 15:09:06

🎯 ALTSEASON PROBABILITY: 90%

✅ BTC dominance < 61%
✅ Others dominance > 30%
✅ Stablecoin dom rejected
⚠️ BTC holding key support

┌─────────────────────┬───────────┬──────────┐
│ Bitcoin Critical Levels                     │
├─────────────────────┼───────────┼──────────┤
│ Critical Low        │ $104,000  │ ✅ Above │
│ Critical High       │ $105,000  │ ✅ Above │
│ Bull Confirmation   │ $116,000  │ ❌ Below │
│ Breakdown           │ $88,000   │ ✅ Above │
│ Current Price       │ $105,917  │ +0.95%   │
└─────────────────────┴───────────┴──────────┘

┌──────────────────────┬─────────┬──────────┐
│ Dominance Metrics                          │
├──────────────────────┼─────────┼──────────┤
│ BTC Dominance        │ 57.68%  │ 🟢 Falling│
│ Others Dominance     │ 30.59%  │ 🟢 Rising │
│ Stablecoin Dom (est) │ 5.00%   │ 📊       │
└──────────────────────┴─────────┴──────────┘
```

## 🛠️ Technical Architecture

### Core Components

1. **Data Collection Layer**
   - CoinGecko API integration (prices, market caps, dominance)
   - Real-time price feeds for BTC, ETH, LTC, and "old coins"
   - Rate-limited API calls with retry logic

2. **Analysis Engine**
   - Proprietary altseason probability algorithm
   - Technical indicator calculations (dominance trends, volume analysis)
   - Multi-factor signal confluence scoring

3. **Alert System**
   - Configurable notification thresholds
   - Multi-channel delivery (terminal, Discord, email)
   - Duplicate alert suppression (30-minute window)

4. **Data Persistence**
   - CSV logging with timestamp granularity
   - Historical pattern analysis capabilities
   - Export-ready format for external tools

### Technology Stack

- **Language**: Python 3.8+
- **Dependencies**: 
  - `requests` - API interactions
  - `rich` - Terminal UI rendering
  - `pyyaml` - Configuration management
  - `pandas` - Data manipulation
- **APIs**: CoinGecko (primary), extensible for others
- **Notifications**: Discord webhooks, SMTP email

## 📥 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Discord account for notifications

### Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/altseason-sentinel.git
cd altseason-sentinel

# Run automated setup
python quick_start.py

# Or manual installation
pip install -r requirements.txt
python altseason_sentinel.py
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Update frequency (seconds)
update_interval_seconds: 300

# Discord notifications
discord:
  enabled: true
  webhook_url: "YOUR_WEBHOOK_URL"

# Email alerts (optional)
email:
  enabled: false
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  from_email: "your@email.com"
  to_email: "your@email.com"
  password: "your_app_password"

# Data logging
logging:
  enabled: true
  file: "altseason_data.csv"
```

## 📊 Data Output

The system generates `altseason_data.csv` with columns:

| Column | Description |
|--------|-------------|
| timestamp | ISO 8601 timestamp |
| btc_price | Bitcoin price (USD) |
| btc_dominance | BTC market cap percentage |
| others_dominance | Altcoin market cap percentage |
| altseason_score | Calculated probability (0-100) |
| ltc_price | Litecoin price (cycle indicator) |

## 🎯 Use Cases

### For Traders
- Identify optimal entry/exit windows for altcoin positions
- Receive alerts for critical BTC support/resistance levels
- Track historical cycle patterns for strategy development

### For Analysts
- Export comprehensive market condition datasets
- Backtest altseason probability algorithm
- Correlate dominance metrics with portfolio performance

### For Developers (Portfolio Demo)
- Demonstrates API integration best practices
- Shows real-time data processing and visualization
- Illustrates multi-channel notification systems
- Example of production-ready Python architecture

## 🔒 Security Notes

- **Never commit `config.yaml` with real credentials**
- Use `.gitignore` to exclude sensitive files
- Discord webhooks should be treated as passwords
- Consider environment variables for production deployments

## 📈 Performance

- API calls: ~3 per update cycle
- Update frequency: Configurable (default 5 minutes)
- Memory footprint: ~50-100MB (including rich terminal rendering)
- CPU usage: Minimal (<1% on modern systems)

## 🛣️ Roadmap

- [ ] Portfolio integration (CoinStats, DeBank APIs)
- [ ] DexScreener live volume tracking
- [ ] Machine learning model for score optimization
- [ ] Web dashboard (React frontend)
- [ ] Mobile app (React Native)
- [ ] Multi-user support with authentication

## 📝 License

MIT License - feel free to use for personal or commercial projects

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Contact

Built by Mike B. - [GitHub Profile](https://github.com/YOUR_USERNAME)

---

## 📸 Screenshots

### Terminal Dashboard
![Dashboard](screenshots/dashboard.png)

### Discord Notifications
![Discord Alerts](screenshots/discord.png)

---

**Note**: This tool is for informational purposes only. Not financial advice. Always do your own research before trading.# altseason-sentinel
Real-time crypto market intelligence dashboard monitoring BTC dominance, altseason signals, and old coin revivals.
