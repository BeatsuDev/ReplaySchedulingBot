



class Game:
    '''
    Class representation of a Rocket League replay of a game.

    Game()
        .playlist
        .date
        .players  # Player objects
    '''
    def __init__(self, data):
        stats = data.read()[:-1]
        stats = [line.split(';') for line in stats.split('\n')]

        players = []

        for player_data in stats[1:]:
                players.append(Player(player_data))


class Replay(Game):
    '''
    Class representation of a Replay file uploaded to ballchasing.com.
    Inherits from core.utils.game.Game()

    Replay(Game)
        .file
        .link
        .author  # Who requested the replay to be uploaded
    '''
    def __init__(self, ID):
        self.link = f'https://ballchasing/replay/{ID}'

        # Check file_checkout.json if the ID already exists in file format
        # Check file_checkout.json for the author
