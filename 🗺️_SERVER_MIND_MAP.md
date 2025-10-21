# 🗺️ Sarlak Academy Bot - Server Mind Map

> **Complete mental map of the production server and codebase**

## 🖥️ Server Overview

### **Server Details**
- **IP**: 163.5.94.227
- **User**: ali
- **Path**: /home/ali/botsarlak
- **Status**: ✅ Active (running)
- **Uptime**: 3h 10min
- **Memory**: 88.8M
- **PID**: 1767916

### **Service Status**
- **Service**: botsarlak.service
- **Status**: ✅ Active (running)
- **Auto-start**: ✅ Enabled
- **Health**: ⚠️ Unhealthy (database connection issue)

---

## 📁 Directory Structure

```
/home/ali/botsarlak/
├── 📄 main.py (38,379 bytes) - Main entry point
├── 📄 main_new.py (11,600 bytes) - Alternative entry
├── 📄 requirements.txt (1,111 bytes) - Dependencies
├── 📄 Makefile (1,516 bytes) - Build commands
├── 📄 .env (570 bytes) - Environment config
├── 📄 bot.log (16.4MB) - Application logs
├── 📁 src/ - Main source code (234 files)
├── 📁 .venv/ - Python virtual environment
├── 📁 logs/ - Log files
├── 📁 archive_20251013_133623/ - Archived files
└── 📁 reference/ - Reference files (symlink)
```

---

## 🏗️ Architecture Overview

### **Core Components**

#### 1. **Entry Points**
- `main.py` - Primary bot entry point
- `main_new.py` - Alternative/experimental entry

#### 2. **Source Code Structure** (`src/`)
```
src/
├── 🎯 handlers/ (83 files) - Bot command handlers
├── 🗄️ database/ (50+ files) - Database schemas & queries
├── ⚙️ utils/ (30+ files) - Utility functions
├── 🎨 keyboards/ (4 files) - Telegram keyboards
├── 🔄 jobs/ (10 files) - Background jobs
├── 📊 monitoring/ (10 files) - Health & monitoring
├── 🎮 services/ (7 files) - Business logic services
├── 🔧 config.py - Configuration management
├── 📱 ux/ (12 files) - User experience components
├── 🧪 tests/ (5 files) - Test files
└── 📊 data/ (4 files) - Static data
```

---

## 🎯 Handler Categories (83 Files)

### **Core Handlers**
- `start_v5.py` - Onboarding & start command
- `profile_v5.py` - User profile management
- `dashboard.py` - Main dashboard
- `main_menu_router.py` - Menu routing

### **Study & Reports**
- `report_v2.py` - Manual study reports
- `study_clean_v2.py` - Study timer
- `daily_report_v5.py` - Daily reports
- `report_integration.py` - Report integration

### **Competition & League**
- `competition_all.py` - Competition system
- `league_v3_handler.py` - League system v3
- `league_v5.py` - League system v5
- `challenges_handler.py` - Challenge system

### **AI & Intelligence**
- `ai_coach_intelligent_handler.py` - AI Coach
- `rank_prediction_v2_handler.py` - Rank prediction

### **Social Features**
- `friend_system.py` - Friend system
- `social_feed.py` - Social feed
- `gift_system.py` - Gift system
- `kudos_handler.py` - Kudos system

### **Education & Content**
- `education_system.py` - Education system
- `flashcard_*.py` - Flashcard system
- `content_menu.py` - Content management

### **Admin & Management**
- `admin_complete.py` - Complete admin panel
- `admin_*.py` - Various admin functions

### **Support & Help**
- `support_v2.py` - Support system
- `help_center.py` - Help center
- `navigation.py` - Navigation helpers

---

## 🗄️ Database Schema (50+ Tables)

### **Core Tables**
- `users` - User accounts (4 users currently)
- `study_sessions` - Study tracking
- `study_reports` - Manual reports
- `daily_closures` - Daily summaries

### **Competition System**
- `competition_challenges` - Competition challenges
- `competition_lists` - Competition lists
- `challenges` - General challenges
- `challenge_participants` - Challenge participants

### **League System**
- `league_divisions_v3` - League divisions
- `division_members` - Division members
- `league_rankings` - League rankings

### **Gamification**
- `badges` - User badges
- `xp_transactions` - XP tracking
- `missions` - Mission system
- `rewards` - Reward system

### **AI & Analytics**
- `ai_insights` - AI insights
- `rank_predictions` - Rank predictions
- `analytics_data` - Analytics data

### **Content & Education**
- `content_lessons` - Educational content
- `courses` - Course structure
- `chapters` - Chapter organization
- `flashcard_decks` - Flashcard decks

### **Social Features**
- `friends` - Friend relationships
- `social_posts` - Social feed posts
- `gifts` - Gift system
- `kudos` - Kudos system

---

## ⚙️ Background Jobs (10 Files)

### **Active Jobs**
- `competition_job.py` - Competition management
- `league_v3_job.py` - League operations
- `mission_system_job.py` - Mission processing
- `news_job.py` - News processing
- `quest_v2_job.py` - Quest system
- `review_reminder_job.py` - Review reminders

### **Monitoring Jobs**
- `inspector_job.py` - System inspection
- `league_report.py` - League reporting

---

## 🔧 Configuration & Environment

### **Environment Variables** (`.env`)
```bash
BOT_TOKEN=7214099093:AAEqEOo2z_iOCo8jDmrw4ZX5FQn3qCjh61k
ADMIN_ID=694245594
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sarlak_academy
DB_USER=postgres
DB_PASSWORD=ali123123
OPENAI_API_KEY=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
```

### **Systemd Service**
- **Service File**: `/etc/systemd/system/botsarlak.service`
- **Status**: Active (running)
- **Auto-start**: Enabled
- **Logs**: `/var/log/botsarlak/`

---

## 📊 Current Status

### **✅ Working Components**
- Bot service is running
- Database is accessible (4 users)
- 50+ database tables exist
- 83 handler files active
- Background jobs operational

### **⚠️ Issues Identified**
- Health endpoint shows "unhealthy"
- Database connection pool issue
- Some handlers may have errors

### **📈 Statistics**
- **Python Files**: 6,644 total
- **Source Files**: 234 in src/
- **Handlers**: 83 active
- **Database Tables**: 50+
- **Users**: 4 registered
- **Log Size**: 16.4MB

---

## 🔍 Key Features Active

### **1. User Management**
- User registration & onboarding
- Profile management
- XP & level system
- Badge system

### **2. Study System**
- Manual study reports
- Study timer
- Daily reports
- Progress tracking

### **3. Competition System**
- Competition challenges
- League system (v3 & v5)
- Rival system
- Ranking system

### **4. AI Features**
- AI Coach
- Rank prediction
- News analysis
- Intelligent insights

### **5. Social Features**
- Friend system
- Social feed
- Gift system
- Kudos system

### **6. Education System**
- Content lessons
- Flashcard system
- Course structure
- Chapter organization

### **7. Admin Panel**
- User management
- Analytics dashboard
- News management
- Support system

---

## 🚨 Critical Issues to Address

### **1. Database Connection**
- Health check shows "disconnected"
- Connection pool not active
- Need to investigate connection.py

### **2. Error Handling**
- Some handlers may have errors
- Need to check bot.log for issues
- Review error tracking

### **3. Performance**
- Large log file (16.4MB)
- Memory usage monitoring
- Database query optimization

---

## 🛠️ Maintenance Commands

### **Service Management**
```bash
# Check status
sudo systemctl status botsarlak

# Restart service
sudo systemctl restart botsarlak

# View logs
sudo journalctl -u botsarlak -f
```

### **Database Management**
```bash
# Connect to database
PGPASSWORD=ali123123 psql -h localhost -U postgres -d sarlak_academy

# Check user count
SELECT COUNT(*) FROM users;

# List all tables
\dt
```

### **Health Monitoring**
```bash
# Health check
curl http://localhost:8080/healthz

# Check logs
tail -f /var/log/botsarlak/bot.log
```

---

## 📋 Quick Reference

### **Important Files**
- `main.py` - Bot entry point
- `src/config.py` - Configuration
- `src/database/connection.py` - Database connection
- `.env` - Environment variables

### **Key Directories**
- `src/handlers/` - Command handlers
- `src/database/` - Database layer
- `src/utils/` - Utilities
- `logs/` - Log files

### **Service Info**
- **Service**: botsarlak.service
- **User**: ali
- **Path**: /home/ali/botsarlak
- **Health**: http://localhost:8080/healthz

---

**Last Updated**: $(date)
**Server Status**: Active but needs database connection fix
**Total Files**: 6,644 Python files
**Active Handlers**: 83
**Database Tables**: 50+
**Users**: 4 registered




