import re
import requests

class game:
    def __init__(self, link):
        self.link = link
        self.game_date = None
        self.scoreboard_by_inning = None
        self.home_team = None
        self.away_team = None
        self.home_play_by_play = None
        self.away_play_by_play = None
        self.home_players_info = None
        self.away_players_info = None

        self.home_aRBI = {}
        self.away_aRBI = {}

        # away_team_runs_by_inning = ['Away: ']
        self.away_scoring_innings = []
        self.away_scoring_inning_plays = {}
        self.runs_by_inning_away = {}

        # home_team_runs_by_inning = ['Home: ']
        self.home_scoring_innings = []
        self.home_scoring_inning_plays = {}
        self.runs_by_inning_home = {}

        self.away_players = {}
        self.runs_remaining_away = {}
        self.home_players = {}
        self.runs_remaining_home = {}
    def parse_json(self):
        json_data = requests.get(self.link).json()
        keys = json_data.keys()

        self.game_date = json_data.get('gameDate')
        self.scoreboard_by_inning = json_data.get('scoreboard').get('linescore').get('innings')
        self.home_team = json_data.get('home_team_data').get('name')

        #data for team is listed when they are pitching, not when they are batting
        self.home_play_by_play = json_data.get('team_away')
        self.away_team = json_data.get('away_team_data').get('name')
        self.away_play_by_play = json_data.get('team_home')

        self.home_players_info = json_data.get('boxscore').get('teams').get('home').get('players').values()
        self.away_players_info = json_data.get('boxscore').get('teams').get('away').get('players').values()

    def get_lineup(self):

        for player_info in self.away_players_info:
            player_id = player_info.get('person').get('id')
            player_name = player_info.get('person').get('fullName')
            player_runs = player_info.get('stats').get('batting').get('runs')
            if player_runs is None:
                player_runs = 0
            self.runs_remaining_away[player_name] = player_runs
            self.away_players[player_name] = player_id
            self.away_aRBI[player_name] = 0

        for player_info in self.home_players_info:
            player_id = player_info.get('person').get('id')
            player_name = player_info.get('person').get('fullName')
            player_runs = player_info.get('stats').get('batting').get('runs')
            if player_runs is None:
                player_runs = 0
            self.runs_remaining_home[player_name] = player_runs
            self.home_players[player_name] = player_id
            self.home_aRBI[player_name] = 0
    def get_scoring_innings(self):

        for inning in self.scoreboard_by_inning:
            runs = inning.get('home').get('runs')
            inningnum = inning.get('num')
            # no runs if bottom of ninth isn't played
            if runs is None:
                continue

            if runs > 0:
                self.home_scoring_innings.append(inningnum)
                self.home_scoring_inning_plays[inningnum] = []
                self.runs_by_inning_home[inningnum] = [runs, []]

            runs = inning.get('away').get('runs')
            #away_team_runs_by_inning.append(runs)
            if runs > 0:
                self.away_scoring_innings.append(inningnum)
                self.away_scoring_inning_plays[inningnum] = []
                self.runs_by_inning_away[inningnum] = [runs,[]]

        for play in self.home_play_by_play:
            inning = play.get('inning')
            if inning in self.home_scoring_innings:
                play_description = [play.get('batter_name'), play.get('des')]
                if len(self.home_scoring_inning_plays[inning]) == 0:
                    self.home_scoring_inning_plays[inning].append(play_description)
                elif len(self.home_scoring_inning_plays[inning]) > 0 and self.home_scoring_inning_plays[inning][-1] != play_description:
                    self.home_scoring_inning_plays[inning].append(play_description)

        for play in self.away_play_by_play:
            inning = play.get('inning')
            if inning in self.away_scoring_innings:
                play_description = [play.get('batter_name'), play.get('des')]
                if len(self.away_scoring_inning_plays[inning]) == 0:
                    self.away_scoring_inning_plays[inning].append(play_description)
                elif len(self.away_scoring_inning_plays[inning]) > 0 and self.away_scoring_inning_plays[inning][-1] != play_description:
                    self.away_scoring_inning_plays[inning].append(play_description)


    def findrunnersthatscore(self, aRBIdict, runs_remaining, runs_by_inning, scoring_inning_plays):

        for inning, plays_list in scoring_inning_plays.items():
            batters_this_inning = []
            for i in range(len(plays_list)):
                batter = plays_list[i][0]
                batters_this_inning.append(batter)
                play_description = plays_list[i][1]
                for player in runs_remaining.keys():
                    run_scored_re = player + '[ ]{0,4}scores'
                    run_finder = re.compile(run_scored_re)
                    match = run_finder.findall(play_description)
                    if len(match) > 0:
                        runs_by_inning[inning][1].append(player)
                        aRBIdict[batter] += len(match)
                        runs_remaining[player] -= 1
                        if runs_remaining[player] < 0:
                            print(player,runs_remaining)
                            print(plays_list)
                            raise Exception("Player cannot have negative runs remaining")

                    homers_scored_re = player + '[ ]{0,4}homers'
                    homer_finder = re.compile(homers_scored_re)
                    match = homer_finder.findall(play_description)
                    if len(match) > 0:
                        runs_by_inning[inning][1].append(player)
                        #aRBIdict[batter] += len(match)
                        runs_remaining[player] -= 1
                        if runs_remaining[player] < 0:
                            print(player, runs_remaining)
                            raise Exception("Player cannot have negative runs remaining")

                    grand_slam_scored_re = player + '.* grand slam'
                    grand_slam_finder = re.compile(grand_slam_scored_re)
                    match = grand_slam_finder.findall(play_description)
                    if len(match) > 0:
                        runs_by_inning[inning][1].append(player)
                        #aRBIdict[batter] += len(match)
                        runs_remaining[player] -= 1
                        if runs_remaining[player] < 0:
                            print(player, runs_remaining)
                            raise Exception("Player cannot have negative runs remaining")
            #print(batters_this_inning)
            #print(inning,runs_by_inning[inning][1])
        runners_that_score = self.adjust_for_uncounted_runners(runs_remaining, runs_by_inning, scoring_inning_plays)
        return runners_that_score

    def adjust_for_uncounted_runners(self,runs_remaining, runs_by_inning, scoring_inning_plays):
        for inning, plays_list in scoring_inning_plays.items():
            runners_that_score = runs_by_inning[inning][1]
            if len(runners_that_score) != runs_by_inning[inning][0]:
                runners_not_accounted_for = [player for player, runs in runs_remaining.items() if runs > 0]
                if len(runners_not_accounted_for) == 1:
                    player = runners_not_accounted_for[0]
                    runs_remaining[player] -= 1
                    runners_that_score.append(player)
                else:
                    raise Exception("ERROR: not all runners accounted for")

        return runners_that_score

    def calculateaRBI(self,runners_that_score, scoring_inning_plays, aRBIdict):
        for inning,plays_list in scoring_inning_plays.items():
            #plays_list = scoring_inning_plays.values()
            for i in range(len(plays_list)-1,-1,-1):
                batter = plays_list[i][0]
                play_description = plays_list[i][1]
                aRBIs = []
                for runner in set(runners_that_score):
                    if runner == batter:
                        continue
                    # batters where runners advance on an error are not given an aRBI
                    runner_to_2nd_on_error_finder = re.compile(runner + '.* to 2nd.* error')
                    match = runner_to_2nd_on_error_finder.findall(play_description)
                    if len(match) == 0:
                        runner_to_2nd_finder = re.compile(runner + ' {0,4}to 2nd')
                        match = runner_to_2nd_finder.findall(play_description)
                        if len(match) > 0:
                            aRBIs.append(runner)
                            aRBIdict[batter] += len(match)

                    # batters where runners advance on an error are not given an aRBI
                    runner_to_3rd_on_error_finder = re.compile(runner + '.* to 3rd.* error')
                    match = runner_to_3rd_on_error_finder.findall(play_description)
                    if len(match) == 0:
                        runner_to_3rd_finder = re.compile(runner + ' {0,4}to 3rd')
                        match = runner_to_3rd_finder.findall(play_description)
                        if len(match) > 0:
                            aRBIs.append(runner)
                            aRBIdict[batter] += len(match)

        # check for batting twice in an inning
        for runner in aRBIs:
            if aRBIs.count(runner) > runners_that_score.count(runner):
                print(aRBIs)
                print(runners_that_score)
                raise Exception("Overcounted a runner")

        for runner in runners_that_score:
            aRBIdict[runner] += 1

