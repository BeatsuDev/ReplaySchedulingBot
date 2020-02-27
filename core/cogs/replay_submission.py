import os, re, time, asyncio

import discord
from discord.ext import commands

class ReplaySubmission(commands.Cog):
    """Cog for Replay Submissions"""
    FORM = ('In-game name:\n'
            'Twitch name:\n'
            'Region:\n'
            'Description:')

    def __init__(self, bot):
        self.bot = bot

        # Users that have invoked the {prefix}form submit command and have
        # 60 seconds to send a form and replays. To prevent double command invokes
        self.waiting_for = []

    @commands.command()
    async def form(self, ctx, *args):
        # If the bot is already waiting for the user to send the form; return
        if self.bot.logger: self.bot.logger.debug(f'{ctx.author.id} issued the `form` command')
        if ctx.author.id in self.waiting_for: return
        if len(args) > 0:

            # `form submit` command
            if args[0].lower()=='submit':
                if not type(ctx.channel) == discord.DMChannel:
                    if self.bot.logger: self.bot.logger.debug(f'{ctx.author.id} `form submit` command was not in a DM')
                    await ctx.send('Send your form in DMs!')
                    return

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

    async def _submit(self, ctx):
        """Submit command"""
        check = lambda m: m.author.id == ctx.author.id
        try:
            self.waiting_for.append(ctx.author.id)
            form = await self.bot.wait_for('message', check=check, timeout=60)
            if self.logger: self.logger.debug(f'Recieved form from {ctx.author.name}#{ctx.author.discriminator}')
        except asyncio.TimeoutError:
            self.waiting_for.remove(ctx.member.id)
            await ctx.send('Timed out')
            return

        try:
            form = self._from_format(form.content)
            if self.logger: self.logger.debug(f'Successfully retrieved form data: {form}')
        except ValueError as e:
            if self.logger: self.logger.debug(f'Error during processing of {ctx.author.name}\'s form: {e}')
            self.waiting_for.remove(ctx.member.id)
            await ctx.send("Couldn't retrieve data from the provided form! Make sure you have copy pasted the form!")
            return

        await ctx.send("Now for the files! Please send both replay files!")
        replays = await self._retrieve_replays(ctx)
        valid, error = await self._check_replays(replays, ctx, form)
        if self.logger: self.logger.debug(f'Checked replays. Error: {error}')

        self.waiting_for.remove(ctx.author.id)
        if valid:
            self._store_replays(form, replays)
            if self.logger: self.logger.info(f'{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) stored 2 replays')
            await ctx.author.send('Your replays have successfully been stored!')
            self.waiting_for.remove(ctx.member.id)
            return

        else:
            await ctx.author.send(f"Your replay wasn't accepted for the following reason: {error}")
            self.waiting_for.remove(ctx.member.id)
            return


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


    async def _retrieve_replays(self, ctx, tempdir='replays/'):
        """Waits for user to send 2 attachments that end with .replay"""
        tasks = []
        check = lambda m: m.author.id == ctx.author.id and len(m.attachments)>0
        while not len(tasks) == 2:
            try:
                rp = await self.bot.wait_for('message', check=check, timeout=45)
            except asyncio.TimeoutError:
                self.waiting_for.remove(ctx.author.id)
                await ctx.send('Timed out')
                return

            for f in rp.attachments:
                if f.filename.endswith('.replay'):
                    # User has sent a .replay file: Process it here
                    dir = tempdir+f.filename

                    # Saving should happen out of the loop so that users don't need to wait
                    # for the replay to finish saving before uploading their second replay.
                    await f.save(dir)
                    rid = self.bot.bc.upload(dir)[1]
                    # So this is the culprit of our mystery
                    # rid gets the value "duplicate replay" here....
                    os.remove(dir)

                    downloadtask = self.bot.loop.create_task(self._ready_replay(rid, author=ctx.author))
                    tasks.append(downloadtask)

        await ctx.send("Awesome! Sit back and relax. The replays are being processed! I'll get back to you soon ;)")
        # Wait for every task to complete
        for task in tasks:
            tout = 120
            try:
                if self.logger: self.logger.debug(f'Attempting to get Replay object from submitted files. Running task: {task}')
                await asyncio.wait_for(task, timeout=120)
                if self.logger: self.logger.debug(f'Completed {task}')

            except asyncio.TimeoutError:
                if self.logger: self.logger.debug(f'Took too long (Timed out) to complete the task: {task}')
                await ctx.send(f'Failed to process within {tout} seconds. Form submission cancelled! Please try again <@{ctx.author.id}>')
                self.waiting_for.remove(ctx.author.id)
                return

        # Tasks should be complete, so time to retrieve the results
        replays = [task.result() for task in tasks]
        return replays


    async def _ready_replay(self, id, interval=30, author=None):
        """Attempts to load a replay repeatedly until succesfull or after 300 seconds has gone.
        (Meant for giving ballchasing.com time to process the replay) In the future this should
        be error handled within Ballchasing.replay() directly."""
        ready = False
        start = time.time()
        while not ready:
            if time.time()-start>120:
                raise asyncio.TimeoutError('Took over 2 minutes to process replays!')
            try:
                if self.logger: self.logger.debug(f'Attempting to get replay from ballchasing with ID: {id}')
                replay = self.bot.bc.replay(id, author=author)
                ready = True
            except KeyError as e:
                # The KeyError arises within the self.bot.bc.replay() function and shouldn't really be handled here
                if self.logger: self.logger.debug(f'Failed to get replay from ballchasing with ID: {id} | Error: {e}')
                await asyncio.sleep(interval)
        return replay


    async def _check_replays(self, form, replays, ctx):
        # form: "list should contain [in_game, twitch_name, region, description] in that order"
        # Function to check if the user is allowed to upload; if the replays aren't ff's etc
        # Should return (bool <valid>, str <error>), so f.ex: (True, None) or (False, "Early FF")
        for r in replays:
            if not form[0] in r.players:
                if not form[0] in [p.steam for p in r.players]:
                    return (False,
                        (f"Player {form[0]} wasn't found in the replay. These folks are in the replay: "
                        f"{r.players}; If you *really* are in this replay, try providing your steam ID "
                        f"instead of `in-game name` in your form"))

            if not r.playlist in ['ranked-standard', 'ranked-solo-standard', 'ranked-doubles', 'ranked-duels']:
                return (False, "Not a ranked 1s, 2s or 3s match")
            if len(r) < 270: return (False, "Early FF (Shorter than 4:30, including goal animation time)")
            if sum([p.goals for p in r.players if p.team == 'orange']) - sum([p.goals for p in r.players if p.team == 'blue']) > 5:
                msg = await ctx.send('The goal difference is really high! Sure you want to send in these replays?')
                await msg.add_reaction('✔️')
                await msg.add_reaction('❌')
                check = lambda r, u: (str(r) == '❌' or str(r) == '✔️') and u.id == ctx.author.id and r.message.id == msg.id
                r, u = await self.bot.wait_for('reaction', check=check)
                return (True, None) if str(r) == '✔️' else (False, 'Large goal difference')
        return (True, None)


    def _store_replays(self, form, replays):
        # form: "list should contain [in_game, twitch_name, region, description] in that order"
        # replays = [Replay(), Replay()]
        pass


def setup(bot):
    bot.add_cog(ReplaySubmission(bot))
    bot.logger.debug("[COG] Added the cog ReplaySubmission to the bot")
