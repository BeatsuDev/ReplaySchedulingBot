import logging
from datetime import datetime as dt

BCLogger = logging.getLogger('BallChasing')

formatter = logging.Formatter('%(asctime)s:%(levelname)s:\t[%(name)s] %(message)s')

shandler = logging.StreamHandler()
shandler.setFormatter(formatter)
shandler.setLevel(logging.DEBUG)

fhandler = logging.FileHandler(f'logs/{dt.now().strftime("%Y-%m-%d_%H-%M")}.log')
fhandler.setFormatter(formatter)
fhandler.setLevel(logging.DEBUG)

BCLogger.addHandler(shandler)
BCLogger.addHandler(fhandler)
BCLogger.setLevel(logging.DEBUG)

# Bot logger
# Same format etc. as BallChasing logger by default

Logger = logging.getLogger('BOT')

formatter = logging.Formatter('%(asctime)s:%(levelname)s:\t[%(name)s] %(message)s')

shandler = logging.StreamHandler()
shandler.setFormatter(formatter)
shandler.setLevel(logging.DEBUG)

fhandler = logging.FileHandler(f'logs/{dt.now().strftime("%Y-%m-%d_%H-%M")}.log')
fhandler.setFormatter(formatter)
fhandler.setLevel(logging.DEBUG)

Logger.addHandler(shandler)
Logger.addHandler(fhandler)
Logger.setLevel(logging.DEBUG)
