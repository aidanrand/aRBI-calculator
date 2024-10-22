

class Team:
    def __init__(self):
        self.link = ""
        self.name = None
        self.play_by_play = None
        self.players_info = None
        self.players = {}
        self.pinch_runners = []
        self.aRBI = {}

        self.scoring_innings = []
        self.scoring_inning_plays = {}
        self.runs_by_inning = {}
        self.runs_remaining = {}
        #self.runners_that_score = {}

