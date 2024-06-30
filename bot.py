import nextcord
import requests
from nextcord.ext import commands, tasks
import revolt
from dotenv import load_dotenv
import os
import json
from io import BytesIO

bot = commands.Bot(command_prefix='!')

load_dotenv()

with open('config.json','r') as file:
    config = json.load(file)

if not "TOKEN_" in os.environ:
    raise RuntimeError('No Discord token found')

@tasks.loop(seconds=120)
async def sync_revolt_emojis():
    rv_guild: revolt.Server = bot.revolt_client.get_server(config['revolt_server'])
    dc_guild: nextcord.Guild = bot.get_guild(config['discord_server'])
    for emoji in rv_guild.emojis:
        for emoji2 in dc_guild.emojis:
            if emoji2.name==emoji.name:
                continue
        url = f'https://autumn.revolt.chat/emojis/{emoji.id}?size=512'
        response = await bot.loop.run_in_executor(None, lambda: requests.get(url))
        emoji_bytes = BytesIO(response.content).read()
        await dc_guild.create_custom_emoji(name=emoji.name, image=emoji_bytes)

@bot.event
async def on_guild_emojis_update(guild, _before, after):
    rv_guild: revolt.Server = bot.revolt_client.get_server(config['revolt_server'])
    if not guild.id==config['discord_server']:
        return
    for emoji in after:
        for emoji2 in rv_guild.emojis:
            if emoji2.name == emoji.name:
                continue
        emoji_bytes = await emoji.read()
        await rv_guild.create_emoji(name=emoji.name, file=revolt.File(emoji_bytes))

@bot.event
async def on_ready():
    print('Bot is ready!')

bot.run(os.environ.get('TOKEN'))
