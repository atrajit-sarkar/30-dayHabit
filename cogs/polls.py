"""
Polls Cog — Scheduled daily habit polls sent via DM at 10 PM.
Handles button interactions and missed response cleanup.
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import asyncio

from utils.firebase_client import (
    get_all_active_users_with_habits, get_habits_needing_poll,
    record_response, record_missed_response, get_all_habits
)
from utils.embeds import (
    create_poll_embed, create_success_embed,
    create_reset_embed, create_penalty_embed
)
from utils.constants import (
    TIMEZONE, POLL_HOUR, POLL_MINUTE, CHALLENGE_DURATION,
    GOOD_HABIT, EMOJI_CHECK, EMOJI_CROSS
)


class HabitPollView(discord.ui.View):
    """
    Persistent view with Yes/No buttons for daily habit polls.
    Each button stores the user_id and habit_id in its custom_id
    so the bot can process responses even after restart.
    """

    def __init__(self, user_id: str, habit_id: str, habit_type: str):
        # Timeout set to 23 hours — after that, treat as missed
        super().__init__(timeout=23 * 3600)
        self.user_id = user_id
        self.habit_id = habit_id
        self.habit_type = habit_type
        self.responded = False

        # Create buttons with custom IDs for persistence
        yes_button = discord.ui.Button(
            label="Yes" if habit_type == GOOD_HABIT else "Yes (Relapsed)",
            style=discord.ButtonStyle.success if habit_type == GOOD_HABIT else discord.ButtonStyle.danger,
            custom_id=f"poll_yes_{user_id}_{habit_id}",
            emoji=EMOJI_CHECK
        )
        no_button = discord.ui.Button(
            label="No" if habit_type == GOOD_HABIT else "No (Resisted)",
            style=discord.ButtonStyle.danger if habit_type == GOOD_HABIT else discord.ButtonStyle.success,
            custom_id=f"poll_no_{user_id}_{habit_id}",
            emoji=EMOJI_CROSS
        )

        yes_button.callback = self.yes_callback
        no_button.callback = self.no_callback

        self.add_item(yes_button)
        self.add_item(no_button)

    async def yes_callback(self, interaction: discord.Interaction):
        """Handle 'Yes' button press."""
        if self.responded:
            await interaction.response.send_message(
                "You've already responded to this poll!", ephemeral=True
            )
            return

        self.responded = True

        # Disable buttons
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        # Record the response
        habit = record_response(self.user_id, self.habit_id, "yes")
        if habit is None:
            await interaction.response.send_message(
                "❌ Error: Habit not found. It may have been deleted.", ephemeral=True
            )
            return

        result = habit.get("result", "")

        if "success" in result:
            embed = create_success_embed(habit)
        elif "reset" in result:
            embed = create_reset_embed(habit)
        elif "penalty" in result:
            embed = create_penalty_embed(habit)
        else:
            embed = create_success_embed(habit)

        await interaction.response.send_message(embed=embed)
        self.stop()

    async def no_callback(self, interaction: discord.Interaction):
        """Handle 'No' button press."""
        if self.responded:
            await interaction.response.send_message(
                "You've already responded to this poll!", ephemeral=True
            )
            return

        self.responded = True

        # Disable buttons
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        # Record the response
        habit = record_response(self.user_id, self.habit_id, "no")
        if habit is None:
            await interaction.response.send_message(
                "❌ Error: Habit not found. It may have been deleted.", ephemeral=True
            )
            return

        result = habit.get("result", "")

        if "success" in result:
            embed = create_success_embed(habit)
        elif "reset" in result:
            embed = create_reset_embed(habit)
        elif "penalty" in result:
            embed = create_penalty_embed(habit)
        else:
            embed = create_success_embed(habit)

        await interaction.response.send_message(embed=embed)
        self.stop()

    async def on_timeout(self):
        """Handle when the user doesn't respond within 23 hours."""
        if not self.responded:
            record_missed_response(self.user_id, self.habit_id)


class Polls(commands.Cog):
    """Sends daily habit polls via DM at 10 PM."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.active_views = {}  # Track active poll views

    def cog_unload(self):
        self.daily_poll.cancel()
        self.missed_response_check.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        """Start the scheduled tasks when the bot is ready."""
        if not self.daily_poll.is_running():
            self.daily_poll.start()
        if not self.missed_response_check.is_running():
            self.missed_response_check.start()
        print(f"📊 Poll system ready. Polls scheduled for {POLL_HOUR}:{POLL_MINUTE:02d} {TIMEZONE}")

    @tasks.loop(hours=24)
    async def daily_poll(self):
        """Send daily polls to all users with active habits via DM."""
        print(f"🔔 Running daily poll at {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S %Z')}")

        try:
            users = get_all_active_users_with_habits()
        except Exception as e:
            print(f"❌ Error fetching users for polling: {e}")
            return

        for user_id, habits in users.items():
            try:
                user = await self.bot.fetch_user(int(user_id))
                if user is None:
                    print(f"⚠️ Could not find user {user_id}")
                    continue

                for habit in habits:
                    # Skip if already polled today
                    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
                    if habit.get("last_poll_date") == today:
                        continue

                    # Calculate day number
                    created_at = habit["created_at"]
                    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is None:
                        created_at = TIMEZONE.localize(created_at)
                    day_number = min(
                        (datetime.now(TIMEZONE) - created_at).days + 1,
                        CHALLENGE_DURATION
                    )

                    # Create poll embed and view
                    embed = create_poll_embed(habit, day_number)
                    view = HabitPollView(user_id, habit["id"], habit["type"])

                    try:
                        dm = await user.send(embed=embed, view=view)
                        self.active_views[f"{user_id}_{habit['id']}"] = view
                        print(f"  ✅ Sent poll to {user.display_name} for '{habit['name']}' (Day {day_number})")
                    except discord.Forbidden:
                        print(f"  ⚠️ Cannot DM user {user.display_name} ({user_id}) — DMs disabled")
                    except Exception as e:
                        print(f"  ❌ Error sending poll to {user_id}: {e}")

                    # Small delay between DMs to avoid rate limits
                    await asyncio.sleep(1)

            except Exception as e:
                print(f"❌ Error processing user {user_id}: {e}")

        print(f"✅ Daily poll cycle complete.")

    @daily_poll.before_loop
    async def before_daily_poll(self):
        """Wait until the bot is ready, then wait until the scheduled time."""
        await self.bot.wait_until_ready()

        now = datetime.now(TIMEZONE)
        target = now.replace(hour=POLL_HOUR, minute=POLL_MINUTE, second=0, microsecond=0)

        # If we've already passed today's poll time, schedule for tomorrow
        if now >= target:
            target += timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        print(f"⏳ Next poll scheduled in {wait_seconds:.0f} seconds "
              f"({target.strftime('%Y-%m-%d %H:%M:%S %Z')})")
        await asyncio.sleep(wait_seconds)

    @tasks.loop(hours=6)
    async def missed_response_check(self):
        """
        Check for polls that were sent but never responded to.
        Runs every 6 hours to catch missed responses.
        """
        # Clean up old views that have timed out
        to_remove = []
        for key, view in self.active_views.items():
            if view.is_finished() and not view.responded:
                to_remove.append(key)

        for key in to_remove:
            del self.active_views[key]

    @missed_response_check.before_loop
    async def before_missed_check(self):
        await self.bot.wait_until_ready()
        # Wait 1 hour after start before first check
        await asyncio.sleep(3600)

    @commands.slash_command(name="test_poll", description="[Test] Receive your daily poll right now, regardless of the time")
    async def test_poll(self, ctx: discord.ApplicationContext):
        """Force send today's poll to the user running the command for testing."""
        await ctx.defer(ephemeral=True)

        try:
            habits = get_all_habits(str(ctx.author.id), active_only=True)
            if not habits:
                await ctx.followup.send("❌ You don't have any active habits. Use `/habit add` first.", ephemeral=True)
                return

            polls_sent = 0
            for habit in habits:
                # Calculate day number
                created_at = habit["created_at"]
                if hasattr(created_at, 'tzinfo') and created_at.tzinfo is None:
                    created_at = TIMEZONE.localize(created_at)
                day_number = min(
                    (datetime.now(TIMEZONE) - created_at).days + 1,
                    CHALLENGE_DURATION
                )

                # Create poll embed and view
                embed = create_poll_embed(habit, day_number)
                view = HabitPollView(str(ctx.author.id), habit["id"], habit["type"])

                try:
                    await ctx.author.send(embed=embed, view=view)
                    self.active_views[f"{ctx.author.id}_{habit['id']}"] = view
                    polls_sent += 1
                except discord.Forbidden:
                    await ctx.followup.send(
                        "⚠️ I couldn't send you a DM. Please enable DMs from server members.",
                        ephemeral=True
                    )
                    return
                except Exception as e:
                    print(f"❌ Error sending test poll: {e}")

            if polls_sent > 0:
                await ctx.followup.send(f"✅ Successfully sent {polls_sent} test poll(s) to your DMs!", ephemeral=True)
            else:
                await ctx.followup.send("❌ Failed to send polls.", ephemeral=True)

        except Exception as e:
            await ctx.followup.send(f"❌ An error occurred: {e}", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Polls(bot))
