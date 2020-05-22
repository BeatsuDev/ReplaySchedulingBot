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

        if BC.logger:
            BC.logger.debug(f"[Game Instanciating] GET request to {self.API}replays/{ID} with headers: {headers}")
            BC.logger.debug(f"[Game Instanciating] Responded with: [{replaydata.status_code}]\n{replaydata.content}")

        self.replaydata = json.loads(replaydata.content)
        self.id = self.replaydata['id']
        self.players = self._get_players()
        self.date = datetime.strptime(self.replaydata.get('date'), '%Y-%m-%dT%H:%M:%SZ')
        self.playlist = self.replaydata.get('playlist_id')
        self.duration = self.replaydata.get('duration')

        if BC.logger:
            BC.logger.debug(f'[Game Instanciating] Fully instanciated game object: {self}!')

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
        self.ID = ID
        self.file = 0

        if kwargs.get('download'): self.file = BC.download(ID)
        self.link = f'https://ballchasing/replay/{ID}'
        self.author = kwargs.get('author')
        self.uploader = self.replaydata['uploader']
        self.title = self.replaydata['title']

        if BC.logger:
            if self.file: BC.logger(f"Replay was downloaded for replay with ID: {ID}")
            BC.logger.debug(f"Replay instance created for replay with ID: {ID}")
            BC.logger.debug(f"Author: {self.author}; Title: {self.title}; Uploader: {self.uploader}")

    def download(self, **kwargs):
        """Downloads the replay file and returns directory to file as a string"""
        if self.file: return self.file

        self.file = BC.download(self.ID, **kwargs)
        return self.file
