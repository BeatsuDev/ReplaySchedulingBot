import requests
import json
import os
import time

from datetime import datetime
from utils.player import Player

class Game:
    """Class representation of a Rocket League replay of a game."""
    API = "https://ballchasing.com/api/"
    def __init__(self, ID, BC):
        headers = {}
        headers['Authorization'] = os.environ.get('BCTOKEN', BC.token)
        replaydata = requests.get(self.API+'replays/'+ID, headers=headers)

        with open('request_logs.txt', 'a+') as f:
            f.write(f"ID ({ID})")
            f.write(f"INCOMING DATA ({time.perf_counter()}):\n{replaydata.content}\n\n")
        import pdb; pdb.set_trace()

        self.replaydata = json.loads(replaydata.content)
        self.id = self.replaydata['id']
        self.players = self._get_players()
        self.date = datetime.strptime(self.replaydata.get('date'), '%Y-%m-%dT%H:%M:%SZ')
        self.playlist = self.replaydata.get('playlist_id')
        self.duration = self.replaydata.get('duration')

    def __len__(self):
        return self.duration


    def _get_players(self):
        players = []
        for P in self.replaydata['blue']['players']:
            kwargs = {
                "team": "blue",
                "name": P.get('name', None),
                "steam": P['id']['id'] if P['id']['platform'] == 'steam' else None,
                "game": self,
                "score": P['stats']['core']['score'],
                "goals": P['stats']['core']['goals'],
                "saves": P['stats']['core']['saves'],
                "camera": P.get('camera'),
                "rank": P.get('rank'),
                "platform": P['id']['platform']
            }
            p = Player(**kwargs)
            players.append(p)


        for P in self.replaydata['orange']['players']:
            kwargs = {
                "team": "orange",
                "name": P.get('name', None),
                "steam": P['id']['id'] if P['id']['platform'] == 'steam' else None,
                "game": self,
                "score": P['stats']['core']['score'],
                "goals": P['stats']['core']['goals'],
                "saves": P['stats']['core']['saves'],
                "camera": P.get('camera', None)
            }
            p = Player(**kwargs)
            players.append(p)
        return players


class Replay(Game):
    """Class representation of a Replay file uploaded to ballchasing.com.
    Inherits from utils.game.Game()
    """
    API = "https://ballchasing.com/api/"
    def __init__(self, ID, BC, **kwargs):
        super().__init__(ID, BC)
        if kwargs.get('download'): self.file = BC.download(ID)
        self.link = f'https://ballchasing/replay/{ID}'
        self.author = kwargs.get('author')
        self.uploader = self.replaydata['uploader']
        self.title = self.replaydata['title']
