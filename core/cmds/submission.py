import time

import discord

from utils.submission.processes import retrieve_ingame, retrieve_twitch, retrieve_region
from utils.submission.processes import retrieve_desc, retrieve_replays, set_replay_info
from utils.submission.errors import *
from utils.submission.gui import embed_desc_al

async def form(ctx, bot):
    desc = (
        f"✅ Discord name | {ctx.author.name}#{ctx.author.discriminator}\n"
        "⭕ In-game name\n"
        "⭕ Twitch Name\n"
        "⭕ Region\n"
        "⭕ Description\n"
        "⭕ Replay name 1\n"
        "⭕ Replay name 2\n"
        "⭕ Playlist\n"
        "⭕ Rank\n"
        "⭕ Platform\n"
    )

    turk = await bot.fetch_user(241993639117586452)
    c = ctx.author.colour if not ctx.author.colour.value == 0x000 else 0xffff00

    gui = discord.Embed(colour=c, description=desc)
    gui.set_author(name=f'You\'re submitting a replay {ctx.author.display_name}!', icon_url=turk.avatar_url)

    guimsg = await ctx.send(embed=gui)

    #try:
    ingame_name = await retrieve_ingame(ctx, guimsg, 1)
    twitch_name = await retrieve_twitch(ctx, guimsg, 2)
    region = await retrieve_region(ctx, guimsg, 3)
    desc = await retrieve_desc(ctx, guimsg, 4)
    replay1, replay2 = await retrieve_replays(ctx, bot, guimsg, 5)


    #except Exception as e:
    #    await ctx.send(f'Error: {e}')
    #    bot.db['waiting'].delete(userid=ctx.author.id)
    #    return

    form = [ingame_name, twitch_name, region, desc]
    replays = [replay1, replay2]

    valid, error = await _check_replays(form, replays, ctx, bot)
    if bot.logger: bot.logger.debug(f'Checked replays. Error: {error}')

    # Check if valid & store replays
    if valid:
        playlist, rank, platform = await set_replay_info(ctx, guimsg, 7, replay1, replay2, ingame_name)

        _store_replays(ctx.author, form, replays, bot)
        if bot.logger: bot.logger.info(f'{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) stored 2 replays')
        await ctx.author.send('Your replays have successfully been stored!')
        return

    else:
        await ctx.author.send(f"Your replay wasn't accepted for the following reason: {error}")
        return

async def _check_replays(form, replays, ctx, bot):
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
            r, u = await bot.wait_for('reaction', check=check)
            return (True, None) if str(r) == '✔️' else (False, 'Large goal difference')
    return (True, None)


def _store_replays(discord_user, form, replays, bot):
    # form: "list should contain [in_game, twitch_name, region, description] in that order"
    # replays = [Replay(), Replay()]
    user = bot.db['users'].upsert(dict(
        id=discord_user.id,
        game_name=form[0],
        twitch_name=form[1],
        region=form[2]
    ), keys=dict(id=discord_user.id))
    bot.logger.info(f'Updated user {discord_user.name}#{discord_user.discriminator} in the database')

    bot.db['entries'].insert(dict(
        userid = discord_user.id,
        added = time.time(),
        update = 0,
        analyzed = 0,
        replay1 = replays[0].ID,
        replay2 = replays[1].ID,
        rank = [p for p in replays[0].players if p.name == form[0]][0].rank,
        description = form[3]
    ))
    bot.logger.info(f'Added replay schedule entry for the discord user {discord_user.name}#{discord_user.discriminator}')
