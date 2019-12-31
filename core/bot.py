import os

import discord
from discord.ext import commands

from utils.ballchasing import Ballchasing

class Turk(commands.Bot):
    def __init__(self):
        super().__init__(commands.when_mentioned_or('turk!'))

        ballchasing_token = os.environ.get('BCTOKEN', '<---- ENTER YOUR BALLCHASING TOKEN ---->')
        self.ballchasing = Ballchasing(ballchasing_token)

    async def load_all_cogs(self):
        for filename in os.listdir('core/cogs/'):
            if filename.endswith('.py'):
                self.load_extension(f'core.cogs.{filename[:-3]}')



    async def on_ready(self):
        print("")
        await self.load_all_cogs()
