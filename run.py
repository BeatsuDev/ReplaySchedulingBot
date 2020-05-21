import os
from core.bot import Turk

if __name__ == '__main__':
    token = os.environ.get('TOKEN', '<-- insert token -->')
    bot = Turk()
    bot.run(token)
