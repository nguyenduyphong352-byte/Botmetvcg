#!/usr/bin/env python3
"""
Discord → Telegram relay.
Listens on a hidden Discord channel, forwards every line to Telegram.
Put your bot tokens in env-vars: DISCORD_TOKEN, TELEGRAM_TOKEN, TG_CHAT_ID
"""
import os, asyncio, discord, telegram
from discord.ext import commands

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_TOKEN = os.getenv("8419273901:AAFgSIEDQLF_P1MaES_29F0mukRQrYSbfp8")
TG_CHAT_ID    = int(os.getenv("7497594902"))

intents = discord.Intents.default(); intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, self_bot=True)
tg = telegram.Bot(TELEGRAM_TOKEN)

@bot.event
async def on_message(m):
    if m.author == bot.user: return
    await tg.send_message(chat_id=TG_CHAT_ID, text=f"{m.author}: {m.content}")

bot.run(DISCORD_TOKEN)
