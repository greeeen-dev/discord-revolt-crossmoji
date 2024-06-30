"""
discord-revolt-crossmoji - A bot to sync emojis between Discord and Revolt
Copyright (C) 2024  Green

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import nextcord
from nextcord.ext import commands
from revolt.ext import commands as rv_commands
import asyncio
import aiohttp
import revolt
import traceback
import time
from utils import log
import hashlib
import random
import string
from dotenv import load_dotenv
import os
import emoji as pymoji
import datetime

load_dotenv() # Do not check success

if not "TOKEN_REVOLT" in os.environ:
    raise RuntimeError('No Revolt token found')

mentions = nextcord.AllowedMentions(everyone=False, roles=False, users=False)

class Revolt(commands.Cog,name='<:revoltsupport:1211013978558304266> Revolt Support'):
    """An extension that enables the bot to run on Revolt. Manages Revolt instance.
    
    Lots of code was taken from Unifier Revolt Support plugin, which I (Green) made too"""
    def __init__(self,bot):
        self.bot = bot
        if not hasattr(self.bot, 'revolt_client'):
            self.bot.revolt_client = None
            self.bot.revolt_session = None
            self.bot.revolt_client_task = asyncio.create_task(self.revolt_boot())
        self.logger = log.buildlogger(self.bot.package, 'revolt.core', self.bot.loglevel)

    class Client(rv_commands.CommandsClient):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.bot = None
            self.logger = None

        def add_logger(self,logger):
            self.logger = logger

        async def get_prefix(self, message: revolt.Message):
            return self.bot.command_prefix

        async def on_ready(self):
            self.logger.info('Revolt client booted!')

    async def revolt_boot(self):
        if self.bot.revolt_client is None:
            while True:
                async with aiohttp.ClientSession() as session:
                    self.bot.revolt_session = session
                    self.bot.revolt_client = self.Client(session, os.environ.get('TOKEN_REVOLT'))
                    self.bot.revolt_client.add_bot(self.bot)
                    print('Booting Revolt client...')
                    try:
                        await self.bot.revolt_client.start()
                    except Exception as e:
                        if not type(e) is RuntimeError or not str(e)=='Session is closed':
                            traceback.print_exc()
                            print('Revolt client failed to boot!')
                        else:
                            break
                self.logger.warn('Revolt client has exited. Rebooting in 10 seconds...')
                try:
                    await asyncio.sleep(10)
                except:
                    self.logger.error('Couldn\'t sleep, exiting loop...')
                    break

def setup(bot):
    bot.add_cog(Revolt(bot))
