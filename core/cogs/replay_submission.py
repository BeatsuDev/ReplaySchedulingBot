import os, re, time, asyncio

import discord
from discord.ext import commands

from core import cmds
from utils.submission.checks import *


class ReplaySubmission(commands.Cog):
    """Cog for Replay Submissions"""
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self.logger = self.bot.logger

    @commands.command(aliases=['submit', 'replayanalysis', 'analysis'])
    @is_not_waiting()
    async def submit_replay(self, ctx, *args):
        '''Guided form to submit a replay for analysis'''
        if self.logger:
            self.logger.debug(f'{ctx.author.id} issued the `form` command')

        if not type(ctx.channel) == discord.DMChannel:
            if self.logger:
                self.logger.debug(
                    f'{ctx.author.id} `form submit` command was not in a DM'
                )
            await ctx.send('This command can only be issued in DMs')
            return




def setup(bot):
    bot.add_cog(ReplaySubmission(bot))
    bot.logger.debug("[COG] Added the cog ReplaySubmission to the bot")
