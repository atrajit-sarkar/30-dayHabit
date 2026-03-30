"""
Constants and configuration for the 30-Day Habit Tracker Bot.
"""

import os
import pytz

# ─── Challenge Settings ───────────────────────────────────────────────
CHALLENGE_DURATION = 30  # days

# ─── Timezone ─────────────────────────────────────────────────────────
TIMEZONE_STR = os.getenv("TIMEZONE", "Asia/Kolkata")
TIMEZONE = pytz.timezone(TIMEZONE_STR)

# Poll time: 10 PM in configured timezone
POLL_HOUR = 22
POLL_MINUTE = 0

# ─── Habit Types ──────────────────────────────────────────────────────
GOOD_HABIT = "good"
BAD_HABIT = "bad"

# ─── Habit Status ─────────────────────────────────────────────────────
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"  # 30 days elapsed

# ─── Colors (Discord embed hex) ──────────────────────────────────────
COLOR_SUCCESS = 0x2ECC71      # Green — positive actions
COLOR_FAILURE = 0xE74C3C      # Red — resets, penalties
COLOR_WARNING = 0xF39C12      # Orange — warnings
COLOR_INFO = 0x3498DB         # Blue — general info
COLOR_GOLD = 0xF1C40F         # Gold — reports & achievements
COLOR_PURPLE = 0x9B59B6       # Purple — habit creation
COLOR_DARK = 0x2C2F33         # Dark — neutral embeds
COLOR_CELEBRATION = 0x00FF7F  # Spring green — 30-day completion

# ─── Emojis ──────────────────────────────────────────────────────────
EMOJI_CHECK = "✅"
EMOJI_CROSS = "❌"
EMOJI_FIRE = "🔥"
EMOJI_TROPHY = "🏆"
EMOJI_STAR = "⭐"
EMOJI_CHART = "📊"
EMOJI_CALENDAR = "📅"
EMOJI_MUSCLE = "💪"
EMOJI_PARTY = "🎉"
EMOJI_WARNING = "⚠️"
EMOJI_SKULL = "💀"
EMOJI_SHIELD = "🛡️"
EMOJI_HEART = "❤️"
EMOJI_BROKEN = "💔"
EMOJI_CROWN = "👑"
EMOJI_ROCKET = "🚀"
EMOJI_HOURGLASS = "⏳"
EMOJI_SPARKLE = "✨"
EMOJI_GOOD = "🟢"
EMOJI_BAD = "🔴"
EMOJI_SKIP = "⬜"
EMOJI_STREAK = "🔥"

# ─── Progress Bar Characters ─────────────────────────────────────────
BAR_FILLED = "█"
BAR_EMPTY = "░"
BAR_LENGTH = 20

# ─── Messages ─────────────────────────────────────────────────────────
MOTIVATIONAL_QUOTES = [
    "The secret of getting ahead is getting started. — Mark Twain",
    "It's not about being the best. It's about being better than you were yesterday.",
    "Small daily improvements are the key to staggering long-term results.",
    "Discipline is choosing between what you want now and what you want most.",
    "Success is the sum of small efforts repeated day in and day out.",
    "You don't have to be extreme, just consistent.",
    "The only bad workout is the one that didn't happen.",
    "Your future self will thank you.",
    "One day or day one. You decide.",
    "Progress, not perfection.",
]

CONGRATULATION_MESSAGES = [
    "🎉 INCREDIBLE! You've conquered the 30-day challenge! You're unstoppable!",
    "🏆 CHAMPION! 30 days of pure dedication! You've proven your strength!",
    "👑 LEGENDARY! You completed all 30 days! The world is yours!",
    "🚀 PHENOMENAL! 30/30 days — you've built an unbreakable habit!",
    "⭐ OUTSTANDING! Perfect 30-day streak! You're an inspiration!",
]

ENCOURAGEMENT_MESSAGES = [
    "Don't be discouraged! Every attempt makes you stronger. Try again! 💪",
    "Progress isn't always linear. You learned, you grew, and that matters! 🌱",
    "The fact that you tried shows your commitment. Ready for round 2? 🔄",
    "Success is falling seven times and getting up eight. You've got this! 🌟",
    "Remember: you're competing with yourself, not anyone else. Keep going! 🎯",
]
