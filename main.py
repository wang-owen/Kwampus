import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Get token from .env
load_dotenv()
TOKEN = os.environ.get("TOKEN")
if TOKEN is None:
    print("ERROR: Invalid token")
    sys.exit()

intents = discord.Intents.default()
intents.message_content = True

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
async def ssjoin(ctx: commands.Context):
    """Join secret santa"""

    guild = ctx.guild
    if guild is None:
        print("ERROR: Invalid guild")
        return

    role = discord.utils.get(guild.roles, name="Gifter")
    if role is None:
        print('"Gifter" role does not exist. Creating role...')
        role = await guild.create_role(
            name="Gifter", colour=discord.Colour.magenta(), mentionable=True
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
        await ctx.send(f'"Gifter" role given to {author.display_name}.')


@bot.command()
async def ssleave(ctx: commands.Context):
    """Join secret santa"""

    guild = ctx.guild
    if guild is None:
        print("ERROR: Invalid guild")
        return

    role = discord.utils.get(guild.roles, name="Gifter")

    author = await guild.fetch_member(ctx.author.id)
    if author is None:
        print("ERROR: Invalid author")
        return
    try:
        await author.remove_roles(role)  # type: ignore
    except discord.Forbidden:
        await ctx.send("I do not have permissions to manage roles!")
    else:
        await ctx.send(f'"Gifter" role removed from {author.display_name}.')


# Start bot
bot.run(TOKEN)
