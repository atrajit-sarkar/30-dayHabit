"""
Rich Discord embed builders for the 30-Day Habit Tracker.
Creates professional-looking embeds for polls, reports, and notifications.
"""

import discord
import random
from datetime import datetime
from utils.constants import *


def _progress_bar(current: int, total: int) -> str:
    """Generate a visual progress bar."""
    if total == 0:
        percentage = 0
    else:
        percentage = current / total
    filled = int(BAR_LENGTH * percentage)
    empty = BAR_LENGTH - filled
    bar = BAR_FILLED * filled + BAR_EMPTY * empty
    pct = int(percentage * 100)
    return f"`{bar}` **{pct}%** ({current}/{total})"


def _daily_log_grid(daily_log: dict, created_at, challenge_duration: int = 30) -> str:
    """Generate a visual calendar grid of daily responses."""
    if hasattr(created_at, 'strftime'):
        start = created_at
    else:
        start = datetime.now(TIMEZONE)

    grid = ""
    for day in range(challenge_duration):
        from datetime import timedelta
        date = (start + timedelta(days=day)).strftime("%Y-%m-%d")
        if date in daily_log:
            if daily_log[date] == "yes":
                grid += EMOJI_CHECK
            else:
                grid += EMOJI_CROSS
        else:
            grid += EMOJI_SKIP

        # Line break every 7 days
        if (day + 1) % 7 == 0:
            grid += "\n"

    return grid


# ─── Poll Embeds ─────────────────────────────────────────────────────

def create_poll_embed(habit: dict, day_number: int) -> discord.Embed:
    """Create the daily poll embed sent via DM."""
    is_good = habit["type"] == GOOD_HABIT
    type_emoji = EMOJI_GOOD if is_good else EMOJI_BAD
    type_label = "Good Habit" if is_good else "Bad Habit"

    if is_good:
        question = f"Did you complete **{habit['name']}** today?"
        color = COLOR_INFO
    else:
        question = f"Did you do **{habit['name']}** today? *(be honest)*"
        color = COLOR_WARNING

    embed = discord.Embed(
        title=f"{EMOJI_CALENDAR} Daily Habit Check-In",
        description=question,
        color=color,
        timestamp=datetime.now(TIMEZONE)
    )

    embed.add_field(
        name=f"{EMOJI_STAR} Habit",
        value=f"**{habit['name']}**",
        inline=True
    )
    embed.add_field(
        name=f"{type_emoji} Type",
        value=type_label,
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_HOURGLASS} Day",
        value=f"**{day_number}** / {CHALLENGE_DURATION}",
        inline=True
    )

    embed.add_field(
        name=f"{EMOJI_STREAK} Current Streak",
        value=f"**{habit['current_streak']}** days",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_TROPHY} Best Streak",
        value=f"**{habit['best_streak']}** days",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_CHART} Progress",
        value=_progress_bar(habit["total_days_completed"], day_number - 1 if day_number > 1 else 0),
        inline=False
    )

    if is_good:
        embed.set_footer(text="✅ Yes = Completed | ❌ No = Missed (streak resets)")
    else:
        embed.set_footer(text="✅ Yes = Relapsed (penalty) | ❌ No = Resisted (streak continues)")

    quote = random.choice(MOTIVATIONAL_QUOTES)
    embed.add_field(
        name=f"{EMOJI_SPARKLE} Quote of the Day",
        value=f"*{quote}*",
        inline=False
    )

    return embed


# ─── Response Embeds ─────────────────────────────────────────────────

def create_success_embed(habit: dict) -> discord.Embed:
    """Embed for successful habit response."""
    is_good = habit["type"] == GOOD_HABIT

    if is_good:
        title = f"{EMOJI_CHECK} Great job! Habit completed!"
        desc = f"**{habit['name']}** — streak continues!"
    else:
        title = f"{EMOJI_SHIELD} Excellent! You resisted!"
        desc = f"**{habit['name']}** — you stayed strong!"

    embed = discord.Embed(
        title=title,
        description=desc,
        color=COLOR_SUCCESS
    )
    embed.add_field(
        name=f"{EMOJI_FIRE} Current Streak",
        value=f"**{habit['current_streak']}** days",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_TROPHY} Best Streak",
        value=f"**{habit['best_streak']}** days",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_CHART} Total Days",
        value=f"**{habit['total_days_completed']}** / {CHALLENGE_DURATION}",
        inline=True
    )

    return embed


def create_reset_embed(habit: dict) -> discord.Embed:
    """Embed for when a good habit is missed (streak reset)."""
    embed = discord.Embed(
        title=f"{EMOJI_BROKEN} Streak Reset",
        description=(
            f"**{habit['name']}** — you missed today.\n"
            f"Your streak has been reset to **0 days**.\n\n"
            f"Don't give up! Start building your streak again tomorrow! {EMOJI_MUSCLE}"
        ),
        color=COLOR_FAILURE
    )
    embed.add_field(
        name=f"{EMOJI_WARNING} Total Resets",
        value=f"**{habit['resets']}**",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_TROPHY} Best Streak",
        value=f"**{habit['best_streak']}** days",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_CHART} Total Days Completed",
        value=f"**{habit['total_days_completed']}** / {CHALLENGE_DURATION}",
        inline=True
    )

    return embed


def create_penalty_embed(habit: dict) -> discord.Embed:
    """Embed for when a bad habit is relapsed (penalty)."""
    embed = discord.Embed(
        title=f"{EMOJI_SKULL} Relapse Detected!",
        description=(
            f"**{habit['name']}** — you gave in today.\n"
            f"A **penalty** has been recorded and your streak resets to **0**.\n\n"
            f"It's okay, dust yourself off and fight again tomorrow! {EMOJI_MUSCLE}"
        ),
        color=COLOR_FAILURE
    )
    embed.add_field(
        name=f"{EMOJI_WARNING} Total Penalties",
        value=f"**{habit['total_penalties']}**",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_WARNING} Total Resets",
        value=f"**{habit['resets']}**",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_TROPHY} Best Streak",
        value=f"**{habit['best_streak']}** days",
        inline=True
    )

    return embed


# ─── Habit List Embeds ───────────────────────────────────────────────

def create_habit_list_embed(habits: list, user_name: str) -> discord.Embed:
    """Create an embed showing all habits for a user."""
    if not habits:
        embed = discord.Embed(
            title=f"{EMOJI_CALENDAR} Your Habits",
            description=(
                "You don't have any habits yet!\n"
                f"Use `/habit add` to start your 30-day challenge! {EMOJI_ROCKET}"
            ),
            color=COLOR_INFO
        )
        return embed

    embed = discord.Embed(
        title=f"{EMOJI_CALENDAR} {user_name}'s Habits",
        description=f"You have **{len(habits)}** habit(s) being tracked.",
        color=COLOR_PURPLE,
        timestamp=datetime.now(TIMEZONE)
    )

    for habit in habits:
        type_emoji = EMOJI_GOOD if habit["type"] == GOOD_HABIT else EMOJI_BAD
        status_emoji = EMOJI_CHECK if habit["status"] == STATUS_ACTIVE else EMOJI_TROPHY

        # Calculate day number
        created_at = habit["created_at"]
        if hasattr(created_at, 'tzinfo') and created_at.tzinfo is None:
            created_at = TIMEZONE.localize(created_at)
        day_number = min((datetime.now(TIMEZONE) - created_at).days + 1, CHALLENGE_DURATION)

        progress = _progress_bar(habit["total_days_completed"], day_number)

        value = (
            f"{type_emoji} Type: **{habit['type'].capitalize()}**\n"
            f"{EMOJI_HOURGLASS} Day: **{day_number}/{CHALLENGE_DURATION}**\n"
            f"{EMOJI_FIRE} Streak: **{habit['current_streak']}** days\n"
            f"{EMOJI_CHART} Progress: {progress}\n"
            f"{status_emoji} Status: **{habit['status'].capitalize()}**"
        )

        embed.add_field(
            name=f"{'━' * 25}\n{habit['name']}",
            value=value,
            inline=False
        )

    return embed


def create_habit_info_embed(habit: dict) -> discord.Embed:
    """Detailed view of a single habit."""
    is_good = habit["type"] == GOOD_HABIT
    type_emoji = EMOJI_GOOD if is_good else EMOJI_BAD
    color = COLOR_SUCCESS if is_good else COLOR_WARNING

    created_at = habit["created_at"]
    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is None:
        created_at = TIMEZONE.localize(created_at)
    day_number = min((datetime.now(TIMEZONE) - created_at).days + 1, CHALLENGE_DURATION)

    embed = discord.Embed(
        title=f"{type_emoji} {habit['name']}",
        description=f"**{habit['type'].capitalize()} Habit** — Day {day_number}/{CHALLENGE_DURATION}",
        color=color,
        timestamp=datetime.now(TIMEZONE)
    )

    embed.add_field(name=f"{EMOJI_FIRE} Current Streak", value=f"**{habit['current_streak']}** days", inline=True)
    embed.add_field(name=f"{EMOJI_TROPHY} Best Streak", value=f"**{habit['best_streak']}** days", inline=True)
    embed.add_field(name=f"{EMOJI_CHECK} Days Completed", value=f"**{habit['total_days_completed']}**", inline=True)
    embed.add_field(name=f"{EMOJI_WARNING} Resets", value=f"**{habit['resets']}**", inline=True)

    if not is_good:
        embed.add_field(name=f"{EMOJI_SKULL} Penalties", value=f"**{habit['total_penalties']}**", inline=True)

    embed.add_field(
        name=f"\n{EMOJI_CHART} Overall Progress",
        value=_progress_bar(habit["total_days_completed"], CHALLENGE_DURATION),
        inline=False
    )

    # Daily log grid
    if habit.get("daily_log"):
        grid = _daily_log_grid(habit["daily_log"], created_at)
        legend = f"{EMOJI_CHECK} = Done  {EMOJI_CROSS} = Missed  {EMOJI_SKIP} = Pending"
        embed.add_field(
            name=f"\n{EMOJI_CALENDAR} Daily Log",
            value=f"{grid}\n{legend}",
            inline=False
        )

    embed.add_field(
        name=f"\n{EMOJI_CALENDAR} Started",
        value=f"<t:{int(created_at.timestamp())}:D>",
        inline=True
    )
    end_ts = int(habit["challenge_end"].timestamp()) if hasattr(habit["challenge_end"], 'timestamp') else 0
    embed.add_field(
        name=f"{EMOJI_HOURGLASS} Ends",
        value=f"<t:{end_ts}:D>",
        inline=True
    )

    return embed


# ─── 30-Day Report Embed ────────────────────────────────────────────

def create_final_report_embed(habit: dict) -> discord.Embed:
    """Create the final 30-day progress report embed."""
    completed_all = habit["total_days_completed"] >= CHALLENGE_DURATION
    is_good = habit["type"] == GOOD_HABIT
    type_emoji = EMOJI_GOOD if is_good else EMOJI_BAD

    if completed_all:
        title = f"{EMOJI_CROWN} 30-DAY CHALLENGE COMPLETE! {EMOJI_CROWN}"
        congrats = random.choice(CONGRATULATION_MESSAGES)
        description = (
            f"**{habit['name']}** — {type_emoji} {habit['type'].capitalize()} Habit\n\n"
            f"{congrats}\n\n"
            f"You've successfully completed all **{CHALLENGE_DURATION} days**! "
            f"This habit is now part of who you are. {EMOJI_SPARKLE}"
        )
        color = COLOR_CELEBRATION
    else:
        title = f"{EMOJI_CHART} 30-Day Challenge Report"
        encouragement = random.choice(ENCOURAGEMENT_MESSAGES)
        description = (
            f"**{habit['name']}** — {type_emoji} {habit['type'].capitalize()} Habit\n\n"
            f"Your 30-day challenge period has ended.\n\n"
            f"{encouragement}"
        )
        color = COLOR_GOLD

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(TIMEZONE)
    )

    # ── Stats Section ──
    embed.add_field(
        name=f"\n{'━' * 30}\n{EMOJI_CHART} STATISTICS",
        value="\u200b",
        inline=False
    )

    embed.add_field(
        name=f"{EMOJI_CHECK} Days Completed",
        value=f"**{habit['total_days_completed']}** / {CHALLENGE_DURATION}",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_TROPHY} Best Streak",
        value=f"**{habit['best_streak']}** days",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_WARNING} Total Resets",
        value=f"**{habit['resets']}**",
        inline=True
    )

    if not is_good:
        embed.add_field(
            name=f"{EMOJI_SKULL} Total Penalties",
            value=f"**{habit['total_penalties']}**",
            inline=True
        )

    # Completion rate
    completion_rate = (habit["total_days_completed"] / CHALLENGE_DURATION) * 100
    embed.add_field(
        name=f"\n{EMOJI_CHART} Completion Rate",
        value=_progress_bar(habit["total_days_completed"], CHALLENGE_DURATION),
        inline=False
    )

    # Daily log grid
    created_at = habit["created_at"]
    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is None:
        created_at = TIMEZONE.localize(created_at)

    if habit.get("daily_log"):
        grid = _daily_log_grid(habit["daily_log"], created_at)
        legend = f"{EMOJI_CHECK} = Done  {EMOJI_CROSS} = Missed  {EMOJI_SKIP} = No Response"
        embed.add_field(
            name=f"\n{EMOJI_CALENDAR} 30-Day Calendar",
            value=f"{grid}\n{legend}",
            inline=False
        )

    # ── Grade ──
    if completion_rate == 100:
        grade = f"{EMOJI_CROWN} **S+ RANK** — PERFECT!"
    elif completion_rate >= 90:
        grade = f"{EMOJI_TROPHY} **A RANK** — Outstanding!"
    elif completion_rate >= 75:
        grade = f"{EMOJI_STAR} **B RANK** — Great effort!"
    elif completion_rate >= 50:
        grade = f"{EMOJI_MUSCLE} **C RANK** — Decent, keep pushing!"
    elif completion_rate >= 25:
        grade = f"{EMOJI_HOURGLASS} **D RANK** — Room for improvement"
    else:
        grade = f"{EMOJI_BROKEN} **F RANK** — Don't give up, try again!"

    embed.add_field(
        name=f"\n{'━' * 30}\n{EMOJI_STAR} FINAL GRADE",
        value=grade,
        inline=False
    )

    # ── Footer ──
    if completed_all:
        embed.set_footer(text="🎉 You are a champion! Share your achievement!")
    else:
        embed.set_footer(text="💪 Use /habit add to start a new challenge!")

    return embed


# ─── Utility Embeds ──────────────────────────────────────────────────

def create_error_embed(message: str) -> discord.Embed:
    """Create a simple error embed."""
    return discord.Embed(
        title=f"{EMOJI_CROSS} Error",
        description=message,
        color=COLOR_FAILURE
    )


def create_info_embed(title: str, message: str) -> discord.Embed:
    """Create a simple info embed."""
    return discord.Embed(
        title=f"{EMOJI_STAR} {title}",
        description=message,
        color=COLOR_INFO
    )


def create_habit_created_embed(habit: dict) -> discord.Embed:
    """Embed shown when a new habit is created."""
    is_good = habit["type"] == GOOD_HABIT
    type_emoji = EMOJI_GOOD if is_good else EMOJI_BAD

    embed = discord.Embed(
        title=f"{EMOJI_ROCKET} New 30-Day Challenge Started!",
        description=(
            f"**{habit['name']}** — {type_emoji} {habit['type'].capitalize()} Habit\n\n"
            f"Your 30-day journey begins now! {EMOJI_SPARKLE}\n"
            f"You'll receive a daily check-in at **10 PM** via DM."
        ),
        color=COLOR_PURPLE,
        timestamp=datetime.now(TIMEZONE)
    )

    if is_good:
        embed.add_field(
            name=f"{EMOJI_CHECK} How it works",
            value=(
                "Each day at 10 PM, I'll ask if you completed this habit.\n"
                f"• **Yes** → Streak continues {EMOJI_FIRE}\n"
                f"• **No** → Streak resets to 0 {EMOJI_BROKEN}\n"
                f"• **No response** → Treated as missed"
            ),
            inline=False
        )
    else:
        embed.add_field(
            name=f"{EMOJI_SHIELD} How it works",
            value=(
                "Each day at 10 PM, I'll ask if you did this bad habit.\n"
                f"• **Yes (relapsed)** → Penalty + streak resets {EMOJI_SKULL}\n"
                f"• **No (resisted)** → Streak continues {EMOJI_FIRE}\n"
                f"• **No response** → Treated as relapse"
            ),
            inline=False
        )

    embed.add_field(
        name=f"{EMOJI_HOURGLASS} Duration",
        value=f"**{CHALLENGE_DURATION} days**",
        inline=True
    )
    embed.add_field(
        name=f"{EMOJI_TROPHY} Goal",
        value=f"Complete all **{CHALLENGE_DURATION}** days!",
        inline=True
    )

    embed.set_footer(text="Good luck! You've got this! 🍀")

    return embed
