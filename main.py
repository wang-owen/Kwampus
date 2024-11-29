import os
import sys
import discord
from discord.ext import commands
from random import shuffle
from datetime import datetime, timedelta
from tzlocal import get_localzone
from dotenv import load_dotenv

COMMAND_PREFIX = "!"

# Get token from .env
load_dotenv()
TOKEN = os.environ.get("TOKEN")
if TOKEN is None:
    print("ERROR: Invalid token")
    sys.exit()

# Enable required intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guild_scheduled_events = True

# Initialize API connection
bot = commands.Bot(COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send("pong")


@bot.command()
async def join(ctx: commands.Context):
    """Join secret santa"""

    guild = ctx.guild
    if guild is None:
        print("ERROR: Invalid guild")
        return

    role = discord.utils.get(guild.roles, name="Secret Santa")
    if role is None:
        print('"Secret Santa" role does not exist. Creating role...')
        role = await guild.create_role(
            name="Secret Santa", colour=discord.Colour.magenta(), mentionable=True
        )

    author = await guild.fetch_member(ctx.author.id)
    if author is None:
        print("ERROR: Invalid author")
        return
    if role in author.roles:
        await ctx.send("You are already enrolled for secret santa!")
        return
    try:
        await author.add_roles(role)
    except discord.Forbidden:
        await ctx.send("I do not have permissions to manage roles!")
    else:
        await ctx.send(f'"Secret Santa" role given to <@{author.id}>.')


@bot.command()
async def leave(ctx: commands.Context):
    """Join secret santa"""

    guild = ctx.guild
    if guild is None:
        print("ERROR: Invalid guild")
        return

    role = discord.utils.get(guild.roles, name="Secret Santa")

    author = await guild.fetch_member(ctx.author.id)
    if author is None:
        print("ERROR: Invalid author")
        return
    if role not in author.roles:
        await ctx.send("You are not enrolled for secret santa!")
        return
    try:
        await author.remove_roles(role)  # type: ignore
    except discord.Forbidden:
        await ctx.send("I do not have permissions to manage roles!")
    else:
        await ctx.send(f'"Secret Santa" role removed from <@{author.id}>.')


@bot.command()
async def setdate(ctx: commands.Context, date: str, *, location: str):
    """Set date and create event for Secret Santa"""

    guild = ctx.guild
    if guild is None:
        print("ERROR: Invalid guild")
        return

    if ctx.author != guild.owner:
        await ctx.send("Date can only be set by the server owner!")
        return

    # Expected format: mm/dd/yyyy/hh/mm
    try:
        # Parse the date string into a datetime object
        date_parts = [int(part) for part in date.split("/")]
        if len(date_parts) != 5:
            raise ValueError("Invalid date format")

        # Validate date parts
        if not (1 <= date_parts[0] <= 12):
            raise ValueError("Month must be between 1 and 12")
        if not (1 <= date_parts[1] <= 31):
            raise ValueError("Day must be between 1 and 31")
        if not (0 <= date_parts[3] < 24):
            raise ValueError("Hour must be between 0 and 23")
        if not (0 <= date_parts[4] < 60):
            raise ValueError("Minute must be between 0 and 59")

        # Get the local timezone
        local_tz = get_localzone()

        # Convert to datetime with local timezone
        scheduled_time = datetime(
            year=date_parts[2],
            month=date_parts[0],
            day=date_parts[1],
            hour=date_parts[3],
            minute=date_parts[4],
            tzinfo=local_tz,
        )

        # Check if the date is in the future
        if scheduled_time <= datetime.now(local_tz):
            await ctx.send("The scheduled date must be in the future!")
            return

        # Create the scheduled event
        event = await guild.create_scheduled_event(
            name="Secret Santa",
            description=":christmas_tree: Prepare to exchange gifts amongst your fellow secret santas! :santa:",
            start_time=scheduled_time,
            end_time=scheduled_time + timedelta(hours=2),
            privacy_level=discord.PrivacyLevel.guild_only,
            entity_type=discord.EntityType.external,
            location=location,
        )
        await ctx.send(
            f"Secret Santa event has been scheduled for {scheduled_time.strftime('%B %d, %Y at %I:%M %p')} at {location}!\n {event.url}"
        )
    except ValueError as e:
        await ctx.send(f"Invalid date format: {date}. Use mm/dd/yyyy/hh/mm. {e}")
    except Exception as e:
        await ctx.send(f"An error occurred while scheduling the event: {e}")


def get_santas(guild: discord.Guild):
    """Return a list of Member with the Secret Santa role.

    Args:
        guild (discord.Guild): guild to query
    """

    role = discord.utils.get(guild.roles, name="Secret Santa")
    if role is not None:
        return role.members
    return None


@bot.command()
async def list(ctx: commands.Context):
    """Get all members with the Secret Santa role"""

    guild = ctx.guild
    if guild is None:
        print("ERROR: Invalid guild")
        return

    santas = get_santas(guild)
    if santas:
        message = "# :santa: Secret Santa List :scroll: \n"
        for santa in santas:
            message += f"* {santa.display_name} (*{santa.name}*)\n"
        await ctx.send(message)
    else:
        await ctx.send("There are no secret santas!")


@bot.command()
async def generate(ctx: commands.Context):
    """Generate Secret Santa ordering and DM each user."""

    guild = ctx.guild
    if guild is None:
        print("ERROR: Invalid guild")
        return

    if ctx.author != guild.owner:
        await ctx.send("Generation can only be initiated by the server owner!")
        return

    santas = get_santas(guild)
    if santas:
        shuffle(santas)
        can_send = []
        cannot_send = []
        for i in range(len(santas)):
            dm = await bot.create_dm(santas[i])
            try:
                await dm.send(
                    ":christmas_tree: Generating Secret Santas... :christmas_tree:"
                )
                if i == len(santas) - 1:
                    can_send.append((dm, santas[0]))
                else:
                    can_send.append((dm, santas[i + 1]))
            except discord.HTTPException:
                cannot_send.append(santas[i])

        if cannot_send:
            for dm, _ in can_send:
                await dm.send(
                    "Oh no! Some users have DM's off. Generation has stopped."
                )
            message = ":exclamation: ERROR: I can't DM the following users!\n"
            for user in cannot_send:
                message += f"* <@{user.id}>\n"
            message += "Please make sure you have enabled DM's from server members!"
            await ctx.send(message)
        else:
            for dm, assigned_to in can_send:
                await dm.send(
                    f":christmas_tree: You are **{assigned_to.display_name}**'s (*{assigned_to.name}*) secret santa! :star:"
                )
            await ctx.send("Secret Santa generation complete! Check your DM's!")
    else:
        await ctx.send("There are no secret santas!")


# Start bot
bot.run(TOKEN)
