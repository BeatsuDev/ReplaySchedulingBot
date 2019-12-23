import os

import discord
from discord.ext import commands

from config import ballchasing_token
from utils.ballchasing import Ballchasing

class Turk(commands.Bot):
    def __init__(self):
        super().__init__(commands.when_mentioned_or('turk!'))
        self.ballchasing = Ballchasing(ballchasing_token)

    async def load_all_cogs(self):
        for filename in os.listdir('core/cogs/'):
            if filename.endswith('.py'):
                self.load_extension(f'core.cogs.{filename[:-3]}')



    async def on_ready(self):
        print("We good to go!")
        await self.load_all_cogs()
