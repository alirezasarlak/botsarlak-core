# 🌌 SarlakBot v3.0 - Gen-Z Cosmic Study Journey

> **Professional Educational Companion for Iranian University Entrance Exam**

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/sarlak-academy/sarlakbot)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](https://t.me/SarlakAcademyBot)

## 🚀 **Vision**

SarlakBot is not just a bot — it's a **journey through the Konkur universe**. Every student who joins starts a personal adventure across planets of growth, motivation, and success. The bot speaks like a **friendly Gen-Z mentor** — chill, emotional, smart, slightly cosmic ✨

## ✨ **Key Features**

### 🌟 **Gen-Z Cosmic Experience**
- **Emotional storytelling** with cosmic journey theme
- **Interactive onboarding** that feels like entering a story
- **Personalized learning paths** based on student profile
- **Viral growth mechanisms** built-in

### 🎯 **Core Modules**
- **🌕 Study Reports** - Track study time, tests, and streaks
- **🪐 Profile System** - Personalized student profiles with progress
- **🌟 Motivation Engine** - Daily quotes and mini missions
- **☄️ Competition System** - Leaderboards and challenges
- **🛍️ Store & Rewards** - Buy courses, books, and packs
- **🧭 Compass** - Rank estimator and university guide

### 🏗️ **Professional Architecture**
- **Clean Architecture** with SOLID principles
- **Modular design** for easy scaling
- **Async/await** throughout
- **Type hints** and comprehensive documentation
- **Zero-downtime updates** with safe migrations

## 🛠️ **Tech Stack**

- **Python 3.10+** with modern async patterns
- **python-telegram-bot v20+** for Telegram integration
- **PostgreSQL** with asyncpg for database
- **Pydantic** for data validation
- **FastAPI** for health monitoring
- **Docker** for containerization

## 🚀 **Quick Start**

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Telegram Bot Token

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sarlak-academy/sarlakbot.git
cd sarlakbot
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Run the bot**
```bash
python main.py
```

## 📁 **Project Structure**

```
src/
├── main.py                 # Bot entry point
├── config.py              # Configuration management
├── utils/                 # Utility functions
│   ├── logging.py         # Professional logging
│   ├── validators.py      # Input validation
│   └── text_utils.py      # Text processing
├── database/              # Database layer
│   ├── connection.py      # Database connection
│   ├── queries.py         # Database queries
│   └── migrations/        # Database migrations
├── handlers/              # Bot handlers
│   ├── onboarding/        # Onboarding flow
│   ├── 🌑_menu/          # Main menu
│   ├── 🪐_profile/       # Profile management
│   ├── 🌕_report/        # Study reports
│   ├── 🌟_motivation/    # Motivation system
│   ├── ☄️_competition/   # Competition system
│   └── 🛍️_store/         # Store & rewards
├── tests/                 # Test suite
├── assets/                # Static assets
│   └── emojis.json        # Emoji definitions
└── docs/                  # Documentation
    ├── ERD.md             # Database schema
    ├── FLOW_ONBOARDING.md # Onboarding flow
    ├── BRAND_GUIDE.md     # Brand guidelines
    └── DEPLOYMENT_PLAN.md # Deployment guide
```

## 🎯 **Onboarding Journey**

The onboarding experience is designed as a cosmic journey:

1. **🌌 Welcome** - Introduction to the cosmic universe
2. **📣 Membership** - Join the academy channel
3. **👤 Identity** - Collect real name and nickname
4. **🎯 Academic** - Select study track and grade
5. **📱 Contact** - Optional phone number
6. **🚀 Launch** - Begin the cosmic journey

## 🗄️ **Database Schema**

The bot uses PostgreSQL with a clean, normalized schema:

- **users** - User accounts and profiles
- **study_sessions** - Study tracking data
- **achievements** - Gamification system
- **competitions** - Competition data
- **content** - Educational content

All migrations are additive-only to preserve data.

## 🔧 **Configuration**

Key configuration options in `.env`:

```bash
# Bot Configuration
BOT_TOKEN=your_bot_token
ADMIN_ID=your_admin_id
REQUIRED_CHANNEL=@sarlak_academy

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=botsarlak
DB_USER=postgres
DB_PASS=your_password

# Feature Flags
FEATURE_ONBOARDING_V1=true
FEATURE_PROFILE_V1=true
FEATURE_REPORT_V1=true
```

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_onboarding.py
```

## 🚀 **Deployment**

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python -m src.database.migrations

# Start the bot
python main.py
```

## 📊 **Monitoring**

- **Health Check**: `http://localhost:8080/healthz`
- **Metrics**: `http://localhost:8080/metrics`
- **Logs**: Structured JSON logging

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 **Support**

- **Telegram**: [@SarlakAcademyBot](https://t.me/SarlakAcademyBot)
- **Channel**: [@Sarlak_academy](https://t.me/Sarlak_academy)
- **Website**: [sarlak.academy](https://sarlak.academy)

## 🎯 **Roadmap**

- [x] **v3.0.0** - Core architecture and onboarding
- [ ] **v3.1.0** - Profile and study tracking
- [ ] **v3.2.0** - Competition system
- [ ] **v3.3.0** - AI coach integration
- [ ] **v3.4.0** - Social features
- [ ] **v3.5.0** - Advanced analytics

---

**Made with ❤️ by Sarlak Academy Team**

*"من هر روز بهترت می‌شناسم، با هم رشد می‌کنیم 🌱"*




