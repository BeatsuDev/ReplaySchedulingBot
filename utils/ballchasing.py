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
        # Grab the replay file
        # Grab the statistics file
        pass

    def upload(self, file):
        post_url = self.BASE + "api/v2/upload"
        headers = {}
        headers['Authorization'] = self.token

        resp = requests.post(post_url, headers=headers, files={'file': file})
        content = json.loads(resp.content)

        if resp.ok:
            return resp.status_code, content['id']
        return resp.status_code, content['error']


    def load_replays(self, directory='replays/'):
        # Load replay objects from directory
        pass


    def file_checkout(self, filedir, ID, file_checkout_dir='replays/file_checkout.json'):
        with open(file_checkout_dir, 'rw') as fc:
