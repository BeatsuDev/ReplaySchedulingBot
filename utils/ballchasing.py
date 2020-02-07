import requests
import json
import re
import os

from utils.game import Replay


class Ballchasing:
    '''Requires a ballchasing.com api token with access to the full ballchasing
    api; granted by Ballchasing.com creator CantFly (from the Ballchasing.com
    discord server)
    '''
    BASE = "https://ballchasing.com/"
    def __init__(self, token, **kwargs):
        self.token = token
        kwargs.get('directory', 'replays')

    def replay(self, ID, output_file='replays/', **kwargs):
        """Downloads the replay with the given ID and returns a Replay object"""
        return Replay(ID, self, **kwargs)


    def download(self, ID, output_file='replays/', name=None):
        """Downloads a replay file from ballchasing"""
        if not name: name = ID
        resp = requests.post(self.BASE + "/dl/replay/" + ID)

        with open(output_file+name+'.replay', 'wb') as f:
            f.write(resp.content)

        return output_file+name+'.replay'

    def upload(self, file):
        """Uploads a file to ballchasing. Returns a tuple with status code and replay ID.
        In case of an error, this function will return the error instead of the ID for the replay
        """
        post_url = self.BASE + "api/v2/upload"
        headers = {}
        headers['Authorization'] = self.token

        if type(file) == str:
            file = open(file, 'rb')

        resp = requests.post(post_url, headers=headers, files={'file': file})
        content = json.loads(resp.content)

        if resp.ok:
            return resp.status_code, content['id']
        elif resp.status_code == 409:
            # Duplicate replays
            return resp.status_code, content['id']

        return resp.status_code, content['error']
