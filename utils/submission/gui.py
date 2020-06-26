
def embed_desc_al(embed, line, append):
    '''
    I honestly can't remember what al stood for. This function changes the given
    line to True, then appends `append` to that line

    '''
    lines = embed.description.split('\n')

    if lines[line][0] == '✔️':
        raise AlreadyChangedError("The line has already been changed to \"Completed\"")

    lines[line][0] = '✔️'
    lines[line] += ' ' + append

    embed.description = '\n'.join(lines)
    return embed
