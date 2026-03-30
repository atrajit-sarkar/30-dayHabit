# 🎯 30-Day Habit Tracker Discord Bot

A professional Discord bot that helps you build good habits and break bad ones through a **30-day challenge system**. Get daily check-in polls via DM, track your streaks, and receive a comprehensive progress report at the end!

## ✨ Features

- 🟢 **Good Habits** — Track habits you want to build (exercise, reading, etc.)
- 🔴 **Bad Habits** — Track habits you want to break (smoking, junk food, etc.)
- 📊 **Daily Polls at 10 PM** — Automated DM check-ins with interactive buttons
- 🔥 **Streak Tracking** — Current streak, best streak, and reset counter
- 📋 **30-Day Reports** — Rich progress reports with grades and calendar views
- 🏆 **Achievement System** — S+ to F rank grading with congratulation messages
- 🔄 **Multiple Habits** — Track as many habits as you want simultaneously
- ☁️ **Firebase Backend** — All data persisted in Firestore
- 🚂 **Railway Ready** — Deploy and forget!

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/habit add <name> <good\|bad>` | Start a new 30-day challenge |
| `/habit list` | View all your habits |
| `/habit info <name>` | Detailed stats for a habit |
| `/habit progress` | Progress overview for active habits |
| `/habit delete <name>` | Remove a habit |
| `/report <name>` | View report for any habit |
| `/ping` | Check bot status |
| `/help` | Learn how to use the bot |

## 🛠️ Setup

### Prerequisites

1. **Python 3.9+**
2. **Discord Bot Token** — [Discord Developer Portal](https://discord.com/developers/applications)
3. **Firebase Project** — [Firebase Console](https://console.firebase.google.com/)

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd 30-dayHabit

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env with your credentials
# Then run:
python bot.py
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DISCORD_TOKEN` | Your Discord bot token |
| `FIREBASE_CREDENTIALS` | Full JSON contents of your Firebase service account key |
| `TIMEZONE` | Your timezone (default: `Asia/Kolkata`) |

## 🚂 Deploy to Railway

1. Push your code to a **GitHub repository**
2. Go to [railway.app](https://railway.app) → Sign in with GitHub
3. **New Project → Deploy from GitHub Repo** → Select your repo
4. Go to **Variables** tab and add:
   - `DISCORD_TOKEN` = your bot token
   - `FIREBASE_CREDENTIALS` = paste entire Firebase JSON
   - `TIMEZONE` = `Asia/Kolkata`
5. Railway auto-detects the `Procfile` and deploys as a worker
6. ✅ Your bot is now running 24/7!

## 🎮 How It Works

### Good Habits (things to DO)
- ✅ **Yes** = You did it! Streak continues 🔥
- ❌ **No** = Missed! Streak resets to 0 💔
- ⬜ **No response** = Treated as missed

### Bad Habits (things to AVOID)
- ✅ **Yes (relapsed)** = Penalty! Streak resets 💀
- ❌ **No (resisted)** = Great! Streak continues 🛡️
- ⬜ **No response** = Treated as relapse

### 30-Day Report
After 30 days, you receive a full report with:
- Total days completed
- Best streak achieved
- Number of resets
- Daily calendar view
- Final grade (S+ to F rank)
- 🎉 Special congratulations for perfect completion!

## 📁 Project Structure

```
30-dayHabit/
├── bot.py                  # Main entry point
├── cogs/
│   ├── habits.py           # Slash commands for habit management
│   ├── polls.py            # Daily poll system (10 PM DMs)
│   └── reports.py          # 30-day progress reports
├── utils/
│   ├── firebase_client.py  # Firebase Firestore operations
│   ├── embeds.py           # Rich Discord embed builders
│   └── constants.py        # Configuration & constants
├── requirements.txt
├── Procfile                # Railway deployment
├── .env.example
└── .gitignore
```

## 📝 License

MIT License
