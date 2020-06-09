from discord.ext import commands

def is_waiting():
    '''
    Returns True if the user has run the form command and is
    going through the replay submission process
    '''
    async def predicate(ctx):
        return True if ctx.bot.db['waiting'].find_one(ctx.author.id) else False
    return commands.check(predicate)

def is_not_waiting():
    '''
    Returns True if the user has not run the form command
    and is not going through the replay submission process
    '''
    async def predicate(ctx):
        return False if ctx.bot.db['waiting'].find_one(ctx.author.id) else True
    return commands.check(predicate)
