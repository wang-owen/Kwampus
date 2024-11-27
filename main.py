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
COMMAND_PREFIX = "!kwampus "
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
    member = ctx.message.author
    guild = ctx.guild
    if guild:
        role = guild.get_role(1311140822447558696)


@bot.command()
async def leave(ctx: commands.Context):
    """Leave secret santa"""
    pass


# Start bot
bot.run(TOKEN)
