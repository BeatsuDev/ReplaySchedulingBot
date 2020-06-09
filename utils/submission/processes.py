import asyncio

def _set_pending_field(guimsg, message):
    gui = guimsg.embeds[0]
    gui.clear_fields()
    gui.add_field(name="Working...", value=message)


def retrieve_id(ctx, guimsg):
    await asyncio.sleep(.5)
    return ctx.author.id

async def retrieve_ingame(ctx, gui):
    gui.
    await ctx.send(embed=gui)
    pass

async def retrieve_twitch(ctx, gui):
    pass

async def retrieve_region(ctx, gui):
    pass

async def retrieve_desc(ctx, gui):
    pass

async def retrieve_replays(ctx, gui):
    pass




async def _submit(self, ctx):
    """Submit command"""

    # Wait for form
    check = lambda m: m.author.id == ctx.author.id
    try:
        self.waiting_for.append(ctx.author.id)
        form = await self.bot.wait_for('message', check=check, timeout=60)
        if self.logger: self.logger.debug(f'Recieved form from {ctx.author.name}#{ctx.author.discriminator}')
    except asyncio.TimeoutError:
        self.waiting_for.remove(ctx.author.id)
        await ctx.send('Timed out')
        return


    # Retrieve data from form
    try:
        form = self._from_format(form.content)
        if self.logger: self.logger.debug(f'Successfully retrieved form data: {form}')
    except ValueError as e:
        if self.error: self.logger.warning(f'Error during processing of {ctx.author.name}\'s form: {e}')
        self.waiting_for.remove(ctx.author.id)
        await ctx.send("Couldn't retrieve data from the provided form! Make sure you have copy pasted the form!")
        return


    # Receive files & check files
    await ctx.send("Now for the files! Please send both replay files!")
    replays = await self._retrieve_replays(ctx)
    valid, error = await self._check_replays(form, replays, ctx)
    if self.logger: self.logger.debug(f'Checked replays. Error: {error}')

    self.waiting_for.remove(ctx.author.id)

    # Check if valid & store replays
    if valid:
        self._store_replays(ctx.author, form, replays)
        if self.logger: self.logger.info(f'{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) stored 2 replays')
        await ctx.author.send('Your replays have successfully been stored!')
        return

    else:
        await ctx.author.send(f"Your replay wasn't accepted for the following reason: {error}")
        self.waiting_for.remove(ctx.author.id)
        return

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
            if self.logger: self.logger.warning(f'Failed to get replay from ballchasing with ID: {id} | Error: {e}')
            await asyncio.sleep(interval)
    return replay


async def _check_replays(self, form, replays, ctx):
    # form: "list should contain [in_game, twitch_name, region, description] in that order"
    # Function to check if the user is allowed to upload; if the replays aren't ff's etc
    # Should return (bool <valid>, str <error>), so f.ex: (True, None) or (False, "Early FF")
    for r in replays:
        if not form[0] in [p.name for p in r.players]:
            if not form[0] in [p.steam for p in r.players]:
                return (False,
                    (f"Player {form[0]} wasn't found in the replay. These folks are in the replay: "
                    f"{[p.name for p in r.players]}; If you *really* are in this replay, try providing your steam ID "
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


def _store_replays(self, discord_user, form, replays):
    # form: "list should contain [in_game, twitch_name, region, description] in that order"
    # replays = [Replay(), Replay()]
    user = self.bot.db['users'].upsert(dict(
        id=discord_user.id,
        game_name=form[0],
        twitch_name=form[1],
        region=form[2]
    ), keys=dict(id=discord_user.id))
    self.logger.info(f'Updated user {discord_user.name}#{discord_user.discriminator} in the database')

    self.bot.db['entries'].insert(dict(
        userid = discord_user.id,
        added = time.time(),
        update = 0,
        analyzed = 0,
        replay1 = replays[0].ID,
        replay2 = replays[1].ID,
        rank = [p for p in replays[0].players if p.name == form[0]][0].rank,
        description = form[3]
    ))
    self.logger.info(f'Added replay schedule entry for the discord user {discord_user.name}#{discord_user.discriminator}')
