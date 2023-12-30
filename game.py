import re
import requests
from team import Team

class Game:
    def __init__(self, link):
        self.link = link
        self.game_date = None
        self.scoreboard_by_inning = None
        self.home = Team()
        self.away = Team()
        # self.home_play_by_play = None
        # self.away_play_by_play = None
        # self.home_players_info = None
        # self.away_players_info = None
        #
        # self.home_aRBI = {}
        # self.away_aRBI = {}
        #
        # self.away_scoring_innings = []
        # self.away_scoring_inning_plays = {}
        # self.runs_by_inning_away = {}
        #
        #
        # self.home_scoring_innings = []
        # self.home_scoring_inning_plays = {}
        # self.runs_by_inning_home = {}
        #
        # self.away_players = {}
        # self.runs_remaining_away = {}
        # self.home_players = {}
        # self.runs_remaining_home = {}
        #
        # self.runners_that_score_home = {}
        # self.runners_that_score_away = {}


    def parse_json(self):
        json_data = requests.get(self.link).json()
        keys = json_data.keys()

        self.game_date = json_data.get('gameDate')
        self.scoreboard_by_inning = json_data.get('scoreboard').get('linescore').get('innings')
        self.home.name = json_data.get('home_team_data').get('name')

        #data for team is listed when they are pitching, not when they are batting
        self.home.play_by_play = json_data.get('team_away')
        self.away.name = json_data.get('away_team_data').get('name')
        self.away.play_by_play = json_data.get('team_home')

        self.home.players_info = json_data.get('boxscore').get('teams').get('home').get('players').values()
        self.away.players_info = json_data.get('boxscore').get('teams').get('away').get('players').values()

    def get_lineup(self, team):

        for player_info in team.players_info:
            player_id = player_info.get('person').get('id')
            player_name = player_info.get('person').get('fullName')
            player_runs = player_info.get('stats').get('batting').get('runs')
            if player_runs is None:
                player_runs = 0
            team.runs_remaining[player_name] = player_runs
            team.players[player_name] = player_id
            team.aRBI[player_name] = 0

        # for player_info in self.home.players_info:
        #     player_id = player_info.get('person').get('id')
        #     player_name = player_info.get('person').get('fullName')
        #     player_runs = player_info.get('stats').get('batting').get('runs')
        #     if player_runs is None:
        #         player_runs = 0
        #     self.home.runs_remaining[player_name] = player_runs
        #     self.home.players[player_name] = player_id
        #     self.home.aRBI[player_name] = 0
    def get_scoring_innings(self):

        for inning in self.scoreboard_by_inning:
            runs = inning.get('home').get('runs')
            inningnum = inning.get('num')
            # no runs if bottom of ninth isn't played
            if runs is None:
                continue

            if runs > 0:
                self.home.scoring_innings.append(inningnum)
                self.home.scoring_inning_plays[inningnum] = []
                self.home.runs_by_inning[inningnum] = [runs, []]

            runs = inning.get('away').get('runs')
            #away_team_runs_by_inning.append(runs)
            if runs > 0:
                self.away.scoring_innings.append(inningnum)
                self.away.scoring_inning_plays[inningnum] = []
                self.away.runs_by_inning[inningnum] = [runs,[]]

        self.get_play_by_play(self.home)
        self.get_play_by_play(self.away)


    def get_play_by_play(self, team):
        for play in team.play_by_play:
            inning = play.get('inning')
            if inning in team.scoring_innings:
                play_description = [play.get('batter_name'), play.get('des')]
                if len(team.scoring_inning_plays[inning]) == 0:
                    team.scoring_inning_plays[inning].append(play_description)
                elif len(team.scoring_inning_plays[inning]) > 0 and team.scoring_inning_plays[inning][-1] != play_description:
                    team.scoring_inning_plays[inning].append(play_description)

        # for play in self.away.play_by_play:
        #     inning = play.get('inning')
        #     if inning in self.away.scoring_innings:
        #         play_description = [play.get('batter_name'), play.get('des')]
        #         if len(self.away.scoring_inning_plays[inning]) == 0:
        #             self.away.scoring_inning_plays[inning].append(play_description)
        #         elif len(self.away.scoring_inning_plays[inning]) > 0 and self.away.scoring_inning_plays[inning][-1] != play_description:
        #             self.away.scoring_inning_plays[inning].append(play_description)


    def findrunnersthatscore(self, team):
            #aRBIdict, runs_remaining, runs_by_inning, scoring_inning_plays,runners_that_score):
        # aRBI = team.aRBI
        # runs_remaining = team.runs_remaining
        # runs_by_inning = team.runs
        for inning, plays_list in team.scoring_inning_plays.items():
            batters_this_inning = []
            for i in range(len(plays_list)):
                batter = plays_list[i][0]
                batters_this_inning.append(batter)
                play_description = plays_list[i][1]
                for player in team.runs_remaining.keys():
                    run_scored_re = player + '[ ]{0,4}scores'
                    run_finder = re.compile(run_scored_re)
                    match = run_finder.findall(play_description)
                    if len(match) > 0:
                        team.runs_by_inning[inning][1].append(player)
                        team.aRBI[batter] += len(match)
                        team.runs_remaining[player] -= 1
                        if team.runs_remaining[player] < 0:
                            print(player,team.runs_remaining)
                            print(plays_list)
                            raise Exception("Player cannot have negative runs remaining")

                    homers_scored_re = player + '[ ]{0,4}homers'
                    homer_finder = re.compile(homers_scored_re)
                    match = homer_finder.findall(play_description)
                    if len(match) > 0:
                        team.runs_by_inning[inning][1].append(player)
                        team.runs_remaining[player] -= 1
                        if team.runs_remaining[player] < 0:
                            print(player, team.runs_remaining)
                            raise Exception("Player cannot have negative runs remaining")

                    grand_slam_scored_re = player + '.* grand slam'
                    grand_slam_finder = re.compile(grand_slam_scored_re)
                    match = grand_slam_finder.findall(play_description)
                    if len(match) > 0:
                        team.runs_by_inning[inning][1].append(player)
                        team.runs_remaining[player] -= 1
                        if team.runs_remaining[player] < 0:
                            print(player, team.runs_remaining)
                            raise Exception("Player cannot have negative runs remaining")

        self.adjust_for_uncounted_runners(team)


    def adjust_for_uncounted_runners(self, team):

        for inning, plays_list in team.scoring_inning_plays.items():
            team.runners_that_score[inning] = team.runs_by_inning[inning][1]
            if len(team.runners_that_score[inning]) != team.runs_by_inning[inning][0]:
                runners_not_accounted_for = [player for player, runs in team.runs_remaining.items() if runs > 0]
                if len(runners_not_accounted_for) == 1:
                    player = runners_not_accounted_for[0]
                    team.runs_remaining[player] -= 1
                    team.runners_that_score[inning].append(player)
                else:
                    raise Exception("ERROR: not all runners accounted for")


    def calculateaRBI(self, team):

        for inning,plays_list in team.scoring_inning_plays.items():
            #plays_list = scoring_inning_plays.values()
            for i in range(len(plays_list)-1,-1,-1):
                batter = plays_list[i][0]
                play_description = plays_list[i][1]
                aRBIs = []
                for runner in set(team.runners_that_score[inning]):
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
                            team.aRBI[batter] += len(match)

                    # batters where runners advance on an error are not given an aRBI
                    runner_to_3rd_on_error_finder = re.compile(runner + '.* to 3rd.* error')
                    match = runner_to_3rd_on_error_finder.findall(play_description)
                    if len(match) == 0:
                        runner_to_3rd_finder = re.compile(runner + ' {0,4}to 3rd')
                        match = runner_to_3rd_finder.findall(play_description)
                        if len(match) > 0:
                            aRBIs.append(runner)
                            team.aRBI[batter] += len(match)

            # check for batting twice in an inning
            for runner in aRBIs:
                if aRBIs.count(runner) > team.runners_that_score[inning].count(runner):
                    print(aRBIs)
                    print(team.runners_that_score)
                    raise Exception("Overcounted a runner")

        for inning, runners in team.runners_that_score.items():
            for runner in runners:
                team.aRBI[runner] += 1

