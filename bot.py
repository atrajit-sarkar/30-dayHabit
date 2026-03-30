"""
30-Day Habit Tracker Discord Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A professional Discord bot that tracks good and bad habits over a 30-day
challenge period. Sends daily polls via DM at 10 PM, records progress
in Firebase Firestore, and generates comprehensive reports.

Author: 30-Day Habit Tracker
License: MIT
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.firebase_client import initialize_firebase
from utils.constants import TIMEZONE, EMOJI_ROCKET, EMOJI_CHECK

# Load environment variables from .env file (local development)
load_dotenv()

# ─── Bot Configuration ───────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True

bot = discord.Bot(
    intents=intents,
    activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="your habits | /habit add"
    ),
    status=discord.Status.online,
)

# ─── Events ──────────────────────────────────────────────────────────


@bot.event
async def on_ready():
    """Called when the bot has connected to Discord."""
    print("━" * 50)
    print(f"  {EMOJI_ROCKET} 30-Day Habit Tracker Bot")
    print(f"  {EMOJI_CHECK} Logged in as: {bot.user.name} ({bot.user.id})")
    print(f"  {EMOJI_CHECK} Connected to {len(bot.guilds)} server(s)")
    print(f"  {EMOJI_CHECK} Timezone: {TIMEZONE}")
    print("━" * 50)


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    """Global error handler for slash commands."""
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(
            f"⏳ Slow down! Try again in **{error.retry_after:.1f}** seconds.",
            ephemeral=True
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.respond(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
    else:
        print(f"❌ Command error: {error}")
        await ctx.respond(
            "❌ Something went wrong. Please try again later.",
            ephemeral=True
        )


# ─── Health Check Command ───────────────────────────────────────────

@bot.slash_command(name="ping", description="Check if the bot is alive")
async def ping(ctx: discord.ApplicationContext):
    """Simple health check command."""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=0x2ECC71
    )
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="help", description="Learn how to use the 30-Day Habit Tracker")
async def help_command(ctx: discord.ApplicationContext):
    """Show how to use the bot."""
    embed = discord.Embed(
        title="📖 30-Day Habit Tracker — Guide",
        description=(
            "Build good habits and break bad ones with a 30-day challenge!\n\n"
            "**How it works:**\n"
            "1️⃣ Add a habit using `/habit add`\n"
            "2️⃣ Every day at **10 PM**, I'll DM you a check-in poll\n"
            "3️⃣ Click **Yes** or **No** to log your day\n"
            "4️⃣ After **30 days**, receive your full progress report!\n"
        ),
        color=0x3498DB
    )

    embed.add_field(
        name="🟢 Good Habits (things to DO)",
        value=(
            "• ✅ **Yes** = You did it! Streak continues 🔥\n"
            "• ❌ **No** = Missed! Streak resets to 0 💔\n"
            "• ⬜ **No response** = Treated as missed"
        ),
        inline=False
    )

    embed.add_field(
        name="🔴 Bad Habits (things to AVOID)",
        value=(
            "• ✅ **Yes (relapsed)** = Penalty! Streak resets 💀\n"
            "• ❌ **No (resisted)** = Great! Streak continues 🛡️\n"
            "• ⬜ **No response** = Treated as relapse"
        ),
        inline=False
    )

    embed.add_field(
        name="📋 Commands",
        value=(
            "`/habit add <name> <good|bad>` — Start a new challenge\n"
            "`/habit list` — View all your habits\n"
            "`/habit info <name>` — Detailed stats for a habit\n"
            "`/habit progress` — Progress overview\n"
            "`/habit delete <name>` — Remove a habit\n"
            "`/report <name>` — View report for a habit\n"
            "`/ping` — Check bot status"
        ),
        inline=False
    )

    embed.set_footer(text="Good luck on your 30-day journey! 🍀")
    await ctx.respond(embed=embed, ephemeral=True)


# ─── Load Cogs & Start ──────────────────────────────────────────────

def main():
    """Initialize Firebase and start the bot."""
    # Initialize Firebase
    try:
        initialize_firebase()
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        print("Make sure FIREBASE_CREDENTIALS environment variable is set correctly.")
        return

    # Load cogs
    cog_extensions = [
        "cogs.habits",
        "cogs.polls",
        "cogs.reports",
    ]

    for ext in cog_extensions:
        try:
            bot.load_extension(ext)
            print(f"  ✅ Loaded cog: {ext}")
        except Exception as e:
            print(f"  ❌ Failed to load cog {ext}: {e}")

    # Get token
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN environment variable is not set!")
        print("Set it in your .env file or Railway environment variables.")
        return

    # Run the bot
    print(f"\n{EMOJI_ROCKET} Starting bot...")
    bot.run(token)


if __name__ == "__main__":
    main()
