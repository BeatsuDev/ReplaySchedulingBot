import os, re, time, asyncio
import arrow

from stuf import stuf

import discord
from discord.ext import commands

class ReplayManagement(commands.Cog):
    """Cog for Replay Submission Managing such as adding, deleting and scheduling"""
    def __init__(self, bot):
        self.bot = bot
        self.logger = self.bot.logger

    @commands.command()
    async def status(self, ctx):
        stufresults = map(stuf, self.bot.db['entries'].find(userid=ctx.author.id))
        entries = list(stufresults)

        desc = ""
        for entry in entries:
            if not entry == entries[0]:
                desc += "\n"
            desc += f"[ID:{entry.id}] Added **{arrow.get(entry.added).humanize()}** | Rank: {entry.rank.name if entry.rank else 'unranked'}"
            desc += f"\n--> *{entry.description}*\n"

        embed = discord.Embed(colour= 0x00ff00 if len(entries) else 0xffff00, description=desc)
        embed.set_author(name=f"Entries for {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ReplayManagement(bot))
    bot.logger.debug("Added the cog ReplayStatus to the bot")
