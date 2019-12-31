import requests
import json
import re


class Ballchasing:
    BASE = "https://ballchasing.com/"

    def __init__(self, token, **kwargs):
        self.token = token

        self.cached_replays = []
        kwargs.get('directory', 'replays')

    def replay(self, ID, output_file='replays/'):
        """Downloads the replay with the given ID and returns a Replay object"""
        # Grab the replay file
        # Grab the statistics file
        pass

    def upload(self, file):
        """Uploads a file to ballchasing. Returns a tuple with status code and replay ID.
        In case of an error, this function will return the error instead of the ID for the replay
        """
        post_url = self.BASE + "api/v2/upload"
        headers = {}
        headers['Authorization'] = self.token

        resp = requests.post(post_url, headers=headers, files={'file': file})
        content = json.loads(resp.content)

        if resp.ok:
            return resp.status_code, content['id']
        return resp.status_code, content['error']


    def load_replays(self, directory='replays/'):
        """Loads replay objects from directory"""
        pass
