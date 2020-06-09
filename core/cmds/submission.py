from utils.submission import processes
from utils.submission.errors import *
from utils.submission.gui import embed_desc_al

def form(ctx, *args, **kwargs):
    desc = (
        "⭕ Discord name\n"
        "⭕ In-game name\n"
        "⭕ Twitch Name\n"
        "⭕ Playlist\n"
        "⭕ Region\n"
        "⭕ Rank\n"
        "⭕ Platform\n"
        "⭕ Description\n"
        "⭕ Replay name 1\n"
        "⭕ Replay name 2\n"
    )

    turk = await self.bot.fetch_user(241993639117586452)
    c = ctx.author.colour if not ctx.author.colour.value == 0x000 else 0xffff00

    gui = discord.Embed(colour=c, description=desc)
    gui.set_author(name=f'You\'re submitting a replay {ctx.author.display_name}!', icon_url=turk.avatar_url)

    guimsg = await ctx.send(embed=gui)

    try:
        discord_id = ctx.author.id

        embed = gui.embed_desc_al(guimsg, )
        await guimsg

        ingame_name = await retrieve_ingame(ctx)
        twitch_name = await retrieve_twitch(ctx)
        region = await retrieve_region(ctx)
        desc = await retrieve_desc(ctx)
        replay1, replay2 = await retrieve_replays(ctx)


    except Exception as e:
        await ctx.send(f'Error: {e}')
        self.db['waiting'].delete(userid=ctx.author.id)
        return
