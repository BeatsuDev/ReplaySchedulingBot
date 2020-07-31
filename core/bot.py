import asyncio, os

import dataset
import discord
from discord.ext import commands

from utils.ballchasing import Ballchasing

# Logging
import logging
from utils import logger
BCLogger = logging.getLogger('BallChasing')
Logger = logging.getLogger('BOT')

Logger.warning('logger on!')

class Turk(commands.Bot):
    def __init__(self):
        super().__init__(commands.when_mentioned_or('turk!'))

        ballchasing_token = os.environ.get('BCTOKEN', '<---- ENTER YOUR BALLCHASING TOKEN ---->')
        self.bc = Ballchasing(ballchasing_token, logger=BCLogger)
        self.logger = Logger
        self.loop = asyncio.get_event_loop()

        # Database
        self.db = dataset.connect(os.environ.get('MAIN_DB', 'sqlite:///mainDB.db'))
        if not self.db['users'].exists: self.db.create_table('users', primary_id='userid')
        if not self.db['entries'].exists: self.db.create_table('entries')
        if not self.db['waiting'].exists: self.db.create_table('waiting')
        if not self.db['scheduled'].exists: self.db.create_table('scheduled')

    async def load_all_cogs(self):
        for filename in os.listdir('core/cogs/'):
            if not filename.endswith('.py'): continue
            try:
                self.load_extension(f'core.cogs.{filename[:-3]}')
                if self.logger:
                    self.logger.debug(f"Loaded bot extension core.cogs.{filename[:-3]}")
            except Exception as e:
                self.logger.warning(f"Failed to load bot extension {filename}. Error: {e}")

    async def on_ready(self):
        print((f'\n\nLogged in as {self.user.name}#{self.user.discriminator};'
            f'connected to {len(self.users)} users through {len(self.guilds)} guilds!'
            ' Invite with link'
            '\nhttps://discordapp.com/api/oauth2/authorize?'
            'client_id=661378621436461056&permissions=124992&scope=bot\n\n'))
        await self.load_all_cogs()
