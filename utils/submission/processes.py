import asyncio, os, time
from utils.submission.gui import embed_desc_al, embed_set_pending
from utils.submission.errors import *

async def retrieve_ingame(ctx, guimsg, line) -> str:
    # Ask and set pending
    await embed_set_pending(guimsg, line)
    qmsg = await ctx.send("What's your IGN (In-game name)? This will be checked later")

    # Answer message
    check = lambda msg: msg.author == ctx.author
    answermsg = await ctx.bot.wait_for('message', check=check)

    # Finished, now set the embed line to finished
    newembed = embed_desc_al(guimsg.embeds[0], line, f"| {answermsg.content.strip()}")
    await guimsg.edit(embed=newembed)

    await qmsg.delete()
    return answermsg.content.strip()

async def retrieve_twitch(ctx, guimsg, line) -> str:
    # Ask and set pending
    await embed_set_pending(guimsg, line)
    qmsg = await ctx.send("What's your name Twitch?")

    check = lambda msg: msg.author == ctx.author
    answermsg = await ctx.bot.wait_for('message', check=check)

    newembed = embed_desc_al(guimsg.embeds[0], line, f"| {answermsg.content.strip()}")
    await guimsg.edit(embed=newembed)

    await qmsg.delete()
    return answermsg.content.strip()

async def retrieve_region(ctx, guimsg, line) -> str:
    # Ask and set pending
    await embed_set_pending(guimsg, line)
    qmsg = await ctx.send("What region do you play in?")

    check = lambda msg: msg.author == ctx.author
    answermsg = await ctx.bot.wait_for('message', check=check)

    newembed = embed_desc_al(guimsg.embeds[0], line, f"| {answermsg.content.strip()}")
    await guimsg.edit(embed=newembed)
    await qmsg.delete()
    return answermsg.content.strip()

async def retrieve_desc(ctx, guimsg, line) -> str:
    # Ask and set pending
    await embed_set_pending(guimsg, line)
    qmsg = await ctx.send("Please send a description for your coaching session.")

    check = lambda msg: msg.author == ctx.author
    answermsg = await ctx.bot.wait_for('message', check=check)

    newembed = embed_desc_al(guimsg.embeds[0], line, f"| {answermsg.content.strip()}")
    await guimsg.edit(embed=newembed)
    await qmsg.delete()
    return answermsg.content.strip()

async def retrieve_replays(ctx, bot, guimsg, line) -> tuple:
    """Waits for user to send 2 attachments that end with .replay"""
    await ctx.send("Time to send your replays! Send your replays here now")

    tempdir = "replays/"

    tasks = []
    check = lambda m: m.author.id == ctx.author.id and len(m.attachments)>0
    while not len(tasks) == 2:
        try:
            rp = await ctx.bot.wait_for('message', check=check, timeout=45)
        except asyncio.TimeoutError:
            await ctx.send('Timed out')
            return

        for f in rp.attachments:
            if f.filename.endswith('.replay'):
                # User has sent a .replay file: Process it here
                dir = tempdir+f.filename

                # Saving should happen out of the loop so that users don't need to wait
                # for the replay to finish saving before uploading their second replay.
                await f.save(dir)
                rid = ctx.bot.bc.upload(dir)[1]
                # So this is the culprit of our mystery
                # rid gets the value "duplicate replay" here....
                os.remove(dir)

                downloadtask = ctx.bot.loop.create_task(_ready_replay(rid, bot, author=ctx.author))
                tasks.append(downloadtask)

    await ctx.send("Awesome! Sit back and relax. The replays are being processed! I'll get back to you soon ;)")
    # Wait for every task to complete
    for task in tasks:
        tout = 120
        try:
            await asyncio.wait_for(task, timeout=tout)

        except asyncio.TimeoutError:
            await ctx.send(f'Failed to process within {tout} seconds. Form submission cancelled! Please try again <@{ctx.author.id}>')
            return

    # Tasks should be complete, so time to retrieve the results
    replays = tuple([task.result() for task in tasks])
    return replays


async def _ready_replay(id, bot, interval=30, author=None):
    """Attempts to load a replay repeatedly until succesfull or after 120 seconds has gone.
    (Meant for giving ballchasing.com time to process the replay) In the future this should
    be error handled within Ballchasing.replay() directly."""
    ready = False
    start = time.time()
    while not ready:
        if time.time()-start>120:
            raise asyncio.TimeoutError('Took over 2 minutes to process replays!')
        try:
            replay = bot.bc.replay(id, author=author)
            ready = True
        except KeyError as e:
            # The KeyError arises within the bot.bc.replay() function and shouldn't really be handled here
            if bot.logger: bot.logger.warning(f'Failed to get replay from ballchasing with ID: {id} | Error: {e}')
            await asyncio.sleep(interval)
    return replay


async def set_replay_info(ctx, guimsg, startline, replay1, replay2, in_game):
    await embed_set_pending(guimsg, startline)
    await embed_set_pending(guimsg, startline+1)
    await embed_set_pending(guimsg, startline+2)

    playlist = replay1.playlist

    newembed = embed_desc_al(guimsg.embeds[0], startline, f"| {playlist}")
    await guimsg.edit(embed= newembed)

    rank = None
    platform = None
    for player in replay1.players:
        if player.name == in_game:
            rank = player.rank
            platform = player.platform

    newembed = embed_desc_al(newembed, startline+1, f"| {rank}")
    newembed = embed_desc_al(newembed, startline+2, f"| {platform}")
    await guimsg.edit(embed=newembed)

    return playlist, rank, platform
