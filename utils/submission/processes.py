import asyncio
from utils.submission.gui import embed_desc_al
from utils.submission.errors import *

async def _set_pending(guimsg, line):
    '''Sets the given line to pending. Just changes the emoji'''
    embed = guimsg.embeds[0]
    lines = embed.description.split('\n')

    if lines[line][0] == '✔️':
        raise AlreadyChangedError("The line has already been changed to \"Completed\"")

    lines[line][0] = '🔄'
    embed.description = '\n'.join(lines)
    await guimsg.edit(embed=embed)

async def retrieve_ingame(ctx, guimsg, line):
    # Ask and set pending
    await _set_pending(guimsg, line)
    await ctx.send("What's your IGN (In-game name)? This will be checked later")

    # Answer message
    check = lambda msg: msg.author == ctx.author
    answermsg = await ctx.bot.wait_for('message', check=check)

    # Finished, now set the embed line to finished
    newembed = embed_desc_al(guimsg.embeds[0], line, f"| {answermsg.content.strip()}")
    await guimsg.edit(embed=newembed)
    return answermsg.content.strip()

async def retrieve_twitch(ctx, guimsg, line):
    # Ask and set pending
    await _set_pending(guimsg, line)
    await ctx.send("What's your name Twitch?")

    check = lambda msg: msg.author == ctx.author
    answermsg = await ctx.bot.wait_for('message', check=check)

    newembed = embed_desc_al(guimsg.embeds[0], line, f"| {answermsg.content.strip()}")
    await guimsg.edit(embed=newembed)
    return answermsg.content.strip()

async def retrieve_region(ctx, guimsg, line):
    # Ask and set pending
    await _set_pending(guimsg, line)
    await ctx.send("What region do you play in?")

    check = lambda msg: msg.author == ctx.author
    answermsg = await ctx.bot.wait_for('message', check=check)

    newembed = embed_desc_al(guimsg.embeds[0], line, f"| {answermsg.content.strip()}")
    await guimsg.edit(embed=newembed)
    return answermsg.content.strip()

async def retrieve_desc(ctx, guimsg, line):
    # Ask and set pending
    await _set_pending(guimsg, line)
    await ctx.send("What region do you play in?")

    check = lambda msg: msg.author == ctx.author
    answermsg = await ctx.bot.wait_for('message', check=check)

    newembed = embed_desc_al(guimsg.embeds[0], line, f"| {answermsg.content.strip()}")
    await guimsg.edit(embed=newembed)
    return answermsg.content.strip()

async def retrieve_replays(ctx, guimsg, line):




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
