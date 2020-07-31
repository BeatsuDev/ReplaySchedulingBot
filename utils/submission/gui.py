from utils.submission.errors import AlreadyChangedError
from discord import Embed

def embed_desc_al(embed, line, append) -> Embed:
    '''
    I honestly can't remember what al stood for. This function changes the given
    line to True, then appends `append` to that line

    '''
    lines = embed.description.split('\n')

    if lines[line][0] == '✅':
        raise AlreadyChangedError("The line has already been changed to \"Completed\"")

    lines[line] = '✅' + lines[line][1:]
    lines[line] += ' ' + append

    embed.description = '\n'.join(lines)
    return embed

async def embed_set_pending(guimsg, line) -> None:
    '''Sets the given line to pending. Just changes the emoji'''
    embed = guimsg.embeds[0]
    lines = embed.description.split('\n')

    if lines[line][0] == '✅':
        raise AlreadyChangedError("The line has already been changed to \"Completed\"")

    lines[line] = '🔄' + lines[line][1:]
    embed.description = '\n'.join(lines)
    await guimsg.edit(embed=embed)
