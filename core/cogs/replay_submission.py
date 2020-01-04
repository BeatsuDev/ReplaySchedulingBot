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

    # Auto-detect form

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot: return


        '''
        if not len(msg.attachments): return

        for f in msg.attachments:
            # Weed out files other than .replay files
            if not f.filename.endswith('.replay'): continue
            if os.path.isfile(f'replays/{f.filename}'):
                await msg.author.send('The file you sent is already submitted')
                continue

            # Save file and update file_checkout.json
            await f.save(open(f'replays/{f.filename}', 'wb'))

            # Upload to Ballchasing
            await msg.author.send('Saved the replay file. Uploading to ballchasing...')
            status, ID = self.bot.ballchasing.upload(open(f'replays/{f.filename}', 'rb'))

            # Send user URL or Error message
            if str(status).startswith("2"):
                url = self.bot.ballchasing.BASE + f"replay/{ID}"
                self.bot.ballchasing.file_checkout(f'replays/{f.filename}', ID)
                await msg.author.send(url)
            elif str(status).startswith("4"):
                await msg.author.send(f'Could not upload file... Error: {ID}')
                os.remove(f'replays/{f.filename}')
        '''

    @commands.command()
    async def form(self, ctx):
        embed = discord.Embed(desc=description, colour=0xffff00)
        await ctx.channel.send(embed=embed)
        await ctx.channel.send(self.form)


def setup(bot):
    bot.add_cog(Test(bot))
    print("[COG] Added cog Test")
