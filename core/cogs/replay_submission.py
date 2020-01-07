import os, re, time, asyncio

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
                if not type(ctx.channel) == discord.DMChannel: return
                await ctx.send('Send your form in DMs!')
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
        """Get data from form formatted string"""
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

        # Return a list; length should be the same as the length of regexps
        # The list should contain [in_game, twitch_name, region, description] in that order
        return [m.group(1).strip() for m in matches]


    async def _submit(self, ctx):
        """Submit command"""
        check = lambda m: m.author.id == ctx.author.id
        try:
            self.waiting_for.append(ctx.author.id)
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
        replays = await self._retrieve_replays(ctx)
        valid, error = await self._check_replays(replays, ctx, form)

        self.waiting_for.remove(ctx.author.id)
        if valid:
            self._store_replays(self, replays)
            await ctx.author.send('Your replays have successfully been stored!')
            return

        else:
            await ctx.author.send(f"Your replay wasn't accepted for the following reason: {error}")
            return


    async def _retrieve_replays(self, ctx, tempdir='replays/'):
        """Waits for user to send 2 attachments that end with .replay"""
        tasks = []
        check = lambda m: m.author.id == ctx.author.id and len(m.attachments)>0
        while not len(tasks) == 2:
            try:
                rp = await self.bot.wait_for('message', check=check, timeout=45)
            except asyncio.TimeoutError:
                self.waiting_for.remove(ctx.member.id)
                await ctx.send('Timed out')
                return

            for f in rp.attachments:
                if f.filename.endswith('.replay'):
                    # User has sent a .replay file: Process it here
                    print(f'tempdir value: {tempdir}')
                    dir = tempdir+f.filename

                    await f.save(dir)
                    rid = self.bot.bc.upload(dir)[1]
                    os.remove(dir)

                    downloadtask = self.bot.loop.create_task(self._ready_replay(rid))
                    tasks.append(downloadtask)

        # Wait for every task to complete
        for task in tasks:
            try:
                asyncio.wait_for(task, timeout=90)
            except asyncio.TimeoutError:
                await ctx.send(f'Failed to process within 90 seconds. Form submission cancelled! Please try again <@{ctx.author.id}>')

        # Tasks should be complete, so time to retrieve the results
        replays = [task.result() for task in tasks]
        return replays


    async def _ready_replay(self, id, interval=5):
        """Attempts to load a replay repeatedly until succesfull or after 120 seconds has gone.
        (Meant for giving ballchasing.com time to process the replay) In the future this should
        be error handled within Ballchasing.replay() directly."""
        ready = False
        start = time.time()
        while not ready:
            if time.time()-start>120:
                raise asyncio.TimeoutError
            try:
                replay = self.bot.bc.replay(id)
                ready = True
            except KeyError:
                await asyncio.sleep(interval)
        return replay


    async def _check_replays(self, replays, ctx, form):
        # Function to check if the user is allowed to upload; if the replays aren't ff's etc
        # Should return (bool <valid>, str <error>)
        pass


def setup(bot):
    bot.add_cog(ReplaySubmission(bot))
    print("[COG] Added the cog ReplaySubmission")
