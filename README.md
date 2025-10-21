# SarlakBot v6 Full - Ultimate Telegram Bot

[![Version](https://img.shields.io/badge/version-v6.1%20Ultimate-blue.svg)](https://github.com/alirezasarlak/botsarlak-core)
[![Status](https://img.shields.io/badge/status-Production%20Ready-green.svg)](https://github.com/alirezasarlak/botsarlak-core)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/alirezasarlak/botsarlak-core)

## 🚀 Quick Deploy

### Server Deployment
```bash
sudo mkdir -p /home/ali/sarlakbot && sudo chown -R ali:ali /home/ali/sarlakbot
# Upload ZIP, then:
cd /home/ali/sarlakbot
unzip SarlakBot_v6_Full.zip
bash scripts/install.sh
cp .env.example .env && nano .env   # fill BOT_TOKEN, ADMIN_ID, DB creds
bash scripts/deploy.sh
journalctl -u sarlakbot -f
```

### Health Check
```bash
source venv/bin/activate
python scripts/smoke_test.py
```

## 📋 Features Overview

### 🏆 League Systems
- **League V3** - 10-level Duolingo-style system (`/leaguev3`)
- **League Advanced** - Advanced league with phoenix system
- **Competition System v2.6** - Latest competitive features (`/compete`)

### 📚 Study Management
- **Flashcards** - Complete flashcard system (`/flashcards`)
- **Study Reports** - Advanced reporting (`/report`)
- **Review Calendar** - Smart review scheduling

### 🎯 User Engagement
- **Missions** - Daily and weekly challenges (`/missions`)
- **Referrals** - Friend invitation system (`/referrals`)
- **Profile** - Complete user management (`/profile`)

### 🏅 Competition Features
- **Rivals List** - Up to 20 competitors (`/rivals`)
- **Head-to-Head** - Direct comparisons
- **Challenges** - 4 types, 6 durations
- **Private Leagues** - 8-character unique codes

## 📊 Project Statistics
- **Files**: 52
- **Code Lines**: 3000+
- **Handlers**: 28
- **Database Tables**: 8
- **Background Jobs**: 4

## 📚 Documentation
- [Complete Documentation](DOCUMENTATION.md) - Full feature overview
- [Version History](VERSION_HISTORY.md) - Development timeline
- [Changelog](CHANGELOG.md) - Detailed changes

## 🔗 Repository
**GitHub**: https://github.com/alirezasarlak/botsarlak-core  
**Status**: ✅ Production Ready  
**Last Updated**: 2025-01-27
