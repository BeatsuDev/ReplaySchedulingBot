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
        # If the bot is already waiting for the user to send the form; return
        if ctx.author.id in self.waiting_for: return
        if len(args) > 0:
            if args[0].lower()=='submit':
                await ctx.send('Send your form here or in DMs!')
                await self._submit(ctx)
                return

        # Assuming there are no args; should just tell the user how to send a form

        embed = discord.Embed(
            title=f'To submit a form, use the command `{self.bot.command_prefix(self.bot, ctx.message)[-1]}form submit`',
            colour=0xffff00)

        embed.set_author(
            icon_url=ctx.message.author.avatar_url,
            name=ctx.message.author.display_name + " is looking to submit a form!")

        embed.set_footer(
            icon_url='https://www.rtk-international.biz/images/Picto/RTK_Pictos_FormulairesServices.png',
            text='Copy paste the form below')

        await ctx.send(embed=embed)
        await ctx.send(self.FORM)

# -----------------------------
# Functions to used in the commands above
# -----------------------------

    def _from_format(self, string):
        regexps = [
            re.compile(r"^In-game name:(?P<in_game>.*)$"),
            re.compile(r"^Twitch name:(?P<twitch_name>.+)$"),
            re.compile(r"^Region:(?P<region>.+)$"),
            re.compile(r"^Description:(?P<description>.+)$")
        ]

        matches = []

        lines = string.split('\n')

        for line in lines:
            line = line.lstrip(' ')
            line = line.strip()
            for expression in regexps:
                result = expression.search(line)
                if result is not None:
                    matches.append(result)

        return [m.group(1).strip() for m in matches]


    async def _submit(self, ctx):
        check = lambda m: m.author.id == ctx.author.id
        try:
            self.waiting_for.append(m.author.id)
            form = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            self.waiting_for.remove(ctx.member.id)
            await ctx.send('Timed out')
            return

        try:
            form = self._from_format(form.content)
        except ValueError as e:
            print(e)
            await ctx.send("Couldn't retrieve data from the provided form! Make sure you have copy pasted the form!")
            return

        await ctx.send("Now for the files! Please send both replay files in one message!")
        replay1, replay2 = await self._retrieve_replays(ctx, form)
        await ctx.send(f"Players in the first replay: {[p.name for p in replay1.players]}")

        self.waiting_for.remove(ctx.author.id)


    async def _retrieve_replays(self, ctx, form, tempdir='replays/'):
        replays = []
        check = lambda m: m.author.id == ctx.author.id
        while not len(replays) == 2:
            try:
                rp = await self.bot.wait_for('message', check=check, timeout=45)
            except asyncio.TimeoutError:
                self.waiting_for.remove(ctx.member.id)
                await ctx.send('Timed out')
                return

            for f in rp.attachments:
                if f.filename.endswith('.replay'):
                    await f.save(tempdir+f.filename)
                    rid = self.bot.bc.upload(tempdir+f.filename)[1]
                    # Give ballchasing 60 seconds to process the replay
                    await ctx.send('Give us 60 seconds for the replay to process')
                    await asyncio.sleep(60)
                    await ctx.send('Go ahead and send the next replay! (unless you have sent 2 already)')
                    replays.append(self.bot.bc.replay(rid))
                    os.remove(tempdir+f.filename)
        return replays


def setup(bot):
    bot.add_cog(ReplaySubmission(bot))
    print("[COG] Added the cog ReplaySubmission")
