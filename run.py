import os
from core.bot import Turk

if __name__ == '__main__':
    token = os.environ.get('TOKEN', '<-- insert token -->')
    bot = Turk()
    import discord
    print(f"Discord version: {discord.__version__}\n")
    bot.run(token)
