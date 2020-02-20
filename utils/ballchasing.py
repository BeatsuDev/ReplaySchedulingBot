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
        self.logger = kwargs.get('logger')
        if self.logger:
            self.logger.debug(f"Created instance of Ballchasing class: {self}")

    def replay(self, ID, output_file='replays/', **kwargs):
        """Downloads the replay with the given ID and returns a Replay object"""
        return Replay(ID, self, **kwargs)


    def download(self, ID, output_dir='replays/', name=None):
        """Downloads a replay file from ballchasing"""
        if not name: name = ID
        resp = requests.post(self.BASE + "/dl/replay/" + ID)
        if self.logger:
            self.logger.debug(f"[Replay Download] Posted to URL \"{self.BASE}/dl/replay/{ID}\".")
            self.logger.debug(f"[Replay Download] Status code: {resp.status_code}")

        with open(output_dir+name+'.replay', 'wb') as f:
            bytes = f.write(resp.content)
            if self.logger:
                self.logger.debug(f"[Replay Download] Wrote {bytes} bytes of data to \"{output_dir}{name}.replay\" for replay with ID: {ID}")

        return output_dir+name+'.replay'

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

        if self.logger:
            self.logger.debug(f"[Replay Upload] Posted to {post_url} with headers {headers} and file {file}")
            self.logger.debug(f"[Replay Upload] Requests responded with:\n[{resp.status_code}]\n{resp.content}")

        if resp.ok:
            if self.logger: self.logger.info(f"[Replay Upload] Successfully uploaded {file}")
            return resp.status_code, content['id']

        elif resp.status_code == 409:
            # Duplicate replays
            if self.logger: self.logger.info(f"[Replay Upload] {file} is already uploaded. (Duplicate)")
            return resp.status_code, content['id']


        if self.logger: self.logger.warning(f"[Replay Upload] Unknown error when uploading {file}")
        return resp.status_code, content['error']
