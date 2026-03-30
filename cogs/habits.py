"""
Habits Cog — Slash commands for creating, listing, viewing, and deleting habits.
"""

import discord
from discord.ext import commands
from discord import SlashCommandGroup, option

from utils.firebase_client import (
    create_habit, get_all_habits, get_habit, delete_habit
)
from utils.embeds import (
    create_habit_list_embed, create_habit_info_embed,
    create_habit_created_embed, create_error_embed, create_info_embed
)
from utils.constants import GOOD_HABIT, BAD_HABIT, EMOJI_ROCKET


class Habits(commands.Cog):
    """Manage your 30-day habit challenges."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    # ─── Slash Command Group ─────────────────────────────────────────
    habit = SlashCommandGroup("habit", "Manage your 30-day habits")

    @habit.command(name="add", description="Start a new 30-day habit challenge")
    @option("name", str, description="Name of the habit (e.g., 'Exercise', 'No Smoking')")
    @option(
        "habit_type",
        str,
        description="Is this a good habit (build) or bad habit (break)?",
        choices=["good", "bad"]
    )
    async def habit_add(self, ctx: discord.ApplicationContext, name: str, habit_type: str):
        """Create a new habit and start the 30-day challenge."""
        await ctx.defer(ephemeral=True)

        habit = create_habit(str(ctx.author.id), name.strip(), habit_type)

        if habit is None:
            embed = create_error_embed(
                f"You already have a habit called **{name}**!\n"
                f"Use `/habit delete {name}` first if you want to restart it."
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return

        embed = create_habit_created_embed(habit)
        await ctx.followup.send(embed=embed, ephemeral=True)

        # Also send a DM to confirm
        try:
            dm_embed = create_info_embed(
                "Challenge Registered!",
                f"Your 30-day challenge for **{name}** ({habit_type} habit) has started!\n\n"
                f"I'll DM you every day at **10 PM** for your check-in. {EMOJI_ROCKET}"
            )
            await ctx.author.send(embed=dm_embed)
        except discord.Forbidden:
            await ctx.followup.send(
                "⚠️ I couldn't send you a DM. Please enable DMs from server members so I can send you daily polls!",
                ephemeral=True
            )

    @habit.command(name="list", description="View all your habits")
    async def habit_list(self, ctx: discord.ApplicationContext):
        """List all habits for the user."""
        await ctx.defer(ephemeral=True)

        habits = get_all_habits(str(ctx.author.id))
        embed = create_habit_list_embed(habits, ctx.author.display_name)
        await ctx.followup.send(embed=embed, ephemeral=True)

    @habit.command(name="info", description="View detailed info about a specific habit")
    @option("name", str, description="Name of the habit to view")
    async def habit_info(self, ctx: discord.ApplicationContext, name: str):
        """Show detailed information about a specific habit."""
        await ctx.defer(ephemeral=True)

        habit = get_habit(str(ctx.author.id), name.strip())
        if habit is None:
            embed = create_error_embed(
                f"No habit found with name **{name}**.\n"
                f"Use `/habit list` to see your habits."
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return

        embed = create_habit_info_embed(habit)
        await ctx.followup.send(embed=embed, ephemeral=True)

    @habit.command(name="delete", description="Delete a habit")
    @option("name", str, description="Name of the habit to delete")
    async def habit_delete(self, ctx: discord.ApplicationContext, name: str):
        """Delete a habit from tracking."""
        await ctx.defer(ephemeral=True)

        deleted = delete_habit(str(ctx.author.id), name.strip())
        if not deleted:
            embed = create_error_embed(
                f"No habit found with name **{name}**.\n"
                f"Use `/habit list` to see your habits."
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return

        embed = create_info_embed(
            "Habit Deleted",
            f"**{name}** has been removed from your tracking.\n"
            f"Use `/habit add` to start a new challenge!"
        )
        await ctx.followup.send(embed=embed, ephemeral=True)

    @habit.command(name="progress", description="View your progress across all active habits")
    async def habit_progress(self, ctx: discord.ApplicationContext):
        """Show progress for all active habits."""
        await ctx.defer(ephemeral=True)

        habits = get_all_habits(str(ctx.author.id), active_only=True)
        if not habits:
            embed = create_info_embed(
                "No Active Habits",
                "You don't have any active habits.\n"
                f"Use `/habit add` to start a new 30-day challenge! {EMOJI_ROCKET}"
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return

        embed = create_habit_list_embed(habits, ctx.author.display_name)
        await ctx.followup.send(embed=embed, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Habits(bot))
