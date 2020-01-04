import os, re, asyncio

import discord
from discord.ext import commands

class ReplaySubmission(commands.Cog):
    """Cog for Replay Submissions"""
    FORM = '''
In-game name:
Twitch name:
Region:
Description:
'''[1:-1]
    def __init__(self, bot):
        self.bot = bot

        # Users that have invoked the {prefix}form submit command and have
        # 60 seconds to send a form and replays. To prevent double command invokes
        self.waiting_for = []

    @commands.command()
    async def form(self, ctx, *args):
        if len(args) > 0:
            if args[0].lower()=='submit':
                await self.submit(ctx)
                return

        embed = discord.Embed(
            title=f'To submit a form, use the command `{self.bot.command_prefix(self.bot, ctx.message)}form submit`',
            colour=0xffff00)

        embed.set_author(
            icon_url=ctx.message.author.avatar_url,
            name=ctx.message.author.display_name + " is looking to submit a form!")

        embed.set_footer(
            icon_url='https://www.rtk-international.biz/images/Picto/RTK_Pictos_FormulairesServices.png',
            text='Copy paste the form below')

        await ctx.channel.send(embed=embed)
        await ctx.channel.send(self.FORM)

    async def submit(ctx):
        # Wait for form string message
        # Retrieve form data
        # Wait for replay files
        # Store in DataBase


def setup(bot):
    bot.add_cog(ReplaySubmission(bot))
    print("[COG] Added cog ReplaySubmission")
