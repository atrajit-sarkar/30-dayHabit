"""
Reports Cog — Handles 30-day challenge completion reports.
Checks periodically for habits that have reached their 30-day mark
and sends the final progress report to the user via DM.
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime
import asyncio

from utils.firebase_client import get_expired_habits, mark_habit_completed
from utils.embeds import create_final_report_embed
from utils.constants import TIMEZONE, CHALLENGE_DURATION


class Reports(commands.Cog):
    """Generates and sends 30-day progress reports."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def cog_unload(self):
        self.check_expired_habits.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        """Start the report checker when the bot is ready."""
        if not self.check_expired_habits.is_running():
            self.check_expired_habits.start()
        print("📋 Report system ready.")

    @tasks.loop(hours=1)
    async def check_expired_habits(self):
        """
        Check every hour for habits that have reached 30 days.
        Send the final progress report and mark as completed.
        """
        print(f"🔍 Checking for completed challenges at {datetime.now(TIMEZONE).strftime('%H:%M:%S %Z')}")

        try:
            expired = get_expired_habits()
        except Exception as e:
            print(f"❌ Error checking expired habits: {e}")
            return

        if not expired:
            return

        for habit in expired:
            user_id = habit.get("user_id")
            if not user_id:
                continue

            try:
                user = await self.bot.fetch_user(int(user_id))
                if user is None:
                    print(f"⚠️ Could not find user {user_id} for report")
                    continue

                # Generate the final report embed
                embed = create_final_report_embed(habit)

                try:
                    await user.send(embed=embed)
                    print(f"  📋 Sent 30-day report to {user.display_name} for '{habit['name']}' "
                          f"({habit['total_days_completed']}/{CHALLENGE_DURATION} days)")
                except discord.Forbidden:
                    print(f"  ⚠️ Cannot DM user {user.display_name} — DMs disabled")
                except Exception as e:
                    print(f"  ❌ Error sending report to {user_id}: {e}")

                # Mark the habit as completed
                mark_habit_completed(user_id, habit["id"])

                # Small delay between reports
                await asyncio.sleep(1)

            except Exception as e:
                print(f"❌ Error processing report for user {user_id}: {e}")

    @check_expired_habits.before_loop
    async def before_check(self):
        """Wait for the bot to be ready before starting checks."""
        await self.bot.wait_until_ready()
        # Wait 2 minutes after startup before first check
        await asyncio.sleep(120)

    # ─── Manual Report Command ───────────────────────────────────────

    @commands.slash_command(name="report", description="View the report for a completed habit")
    @discord.option("name", str, description="Name of the habit")
    async def report(self, ctx: discord.ApplicationContext, name: str):
        """Manually generate a report for any habit (active or completed)."""
        await ctx.defer(ephemeral=True)

        from utils.firebase_client import get_habit
        from utils.embeds import create_error_embed

        habit = get_habit(str(ctx.author.id), name.strip())
        if habit is None:
            embed = create_error_embed(
                f"No habit found with name **{name}**.\n"
                f"Use `/habit list` to see your habits."
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return

        embed = create_final_report_embed(habit)
        await ctx.followup.send(embed=embed, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Reports(bot))
