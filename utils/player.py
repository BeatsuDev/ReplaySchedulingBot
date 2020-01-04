


class Player:
    '''
    A class representation of a Rocket League player in a game.

    # Stats:
        - Name
        - Steam ID
        - Game in which the player is playing in
        - Points
        - Goals
        - Saves
    '''
    def __init__(self, *args, **kwargs):
        self.team = kwargs.get('team')
        self.name = kwargs.get('name')
        self.steam = kwargs.get('steam')
        self.game = kwargs.get('game')
        self.score = kwargs.get('score')
        self.goals = kwargs.get('goals')
        self.saves = kwargs.get('saves')
        self.camera = kwargs.get('camera')
        self.rank = kwargs.get('rank')
