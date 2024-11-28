import os
import sys
import discord
from discord.ext import commands
from random import shuffle
from dotenv import load_dotenv

# Get token from .env
load_dotenv()
TOKEN = os.environ.get("TOKEN")
if TOKEN is None:
    print("ERROR: Invalid token")
    sys.exit()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
COMMAND_PREFIX = "!"
bot = commands.Bot(COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.command()
async def hello(ctx: commands.Context):
    await ctx.send("Hello!")


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
    try:
        await author.add_roles(role)
    except discord.Forbidden:
        await ctx.send("I do not have permissions to manage roles!")
    else:
        await ctx.send(f'"Secret Santa" role given to @{author.name}.')


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
    try:
        await author.remove_roles(role)  # type: ignore
    except discord.Forbidden:
        await ctx.send("I do not have permissions to manage roles!")
    else:
        await ctx.send(f'"Secret Santa" role removed from @{author.name}.')


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
            message += f"* {santa.display_name}\n"
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
            message = ":warning: ERROR: I can't DM the following users!\n"
            for user in cannot_send:
                message += f"* @{user.name}\n"
            message += "Please make sure you have enabled DM's from server members!"
            await ctx.send(message)
        else:
            for dm, assigned_to in can_send:
                await dm.send(
                    f":christmas_tree: You are {assigned_to.display_name}'s ({assigned_to.name}) secret santa! :star:"
                )
    else:
        await ctx.send("There are no secret santas!")


# Start bot
bot.run(TOKEN)
