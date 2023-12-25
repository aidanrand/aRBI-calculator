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

    def parse_json(self):
        json_data = requests.get(game.link).json()
        keys = json_data.keys()

        self.game_date = json_data.get('gameDate')
        self.scoreboard_by_inning = json_data.get('scoreboard').get('linescore').get('innings')
        self.home_team = json_data.get('home_team_data').get('name')

        #data for team is listed when they are pitching, not when they are batting
        self.home_play_by_play = json_data.get('team_away')
        self.away_team = json_data.get('away_team_data').away_team_data.get('name')
        self.away_play_by_play = json_data.get('team_home')

        self.home_player_info = json_data.get('boxscore').get('teams').get('home').get('players').values()
        self.away_player_info = json_data.get('boxscore').get('teams').get('away').get('players').values()

    def get_lineup(self):
        away_players = {}
        #away_aRBI = {}
        runs_remaining_away = {}
        for player_info in self.away_players_info:
            player_id = player_info.get('person').get('id')
            player_name = player_info.get('person').get('fullName')
            player_runs = player_info.get('stats').get('batting').get('runs')
            if player_runs is None:
                player_runs = 0
            runs_remaining_away[player_name] = player_runs
            away_players[player_name] = player_id
            self.away_aRBI[player_name] = 0

        home_players = {}
        #home_aRBI = {}
        runs_remaining_home = {}
        for player_info in self.home_players_info:
            player_id = player_info.get('person').get('id')
            player_name = player_info.get('person').get('fullName')
            player_runs = player_info.get('stats').get('batting').get('runs')
            if player_runs is None:
                player_runs = 0
            runs_remaining_home[player_name] = player_runs
            home_players[player_name] = player_id
            self.home_aRBI[player_name] = 0

        #away_team_runs_by_inning = ['Away: ']
        away_scoring_innings = []
        away_scoring_inning_plays = {}
        runs_by_inning_away = {}

        #home_team_runs_by_inning = ['Home: ']
        home_scoring_innings = []
        home_scoring_inning_plays = {}
        runs_by_inning_home = {}

        for inning in self.scoreboard_by_inning:
            runs = inning.get('home').get('runs')
            inningnum = inning.get('num')
            # no runs if bottom of ninth isn't played
            if runs is None:
                continue

            if runs > 0:
                home_scoring_innings.append(inningnum)
                home_scoring_inning_plays[inningnum] = []
                runs_by_inning_home[inningnum] = [runs, []]

            runs = inning.get('away').get('runs')
            #away_team_runs_by_inning.append(runs)
            if runs > 0:
                away_scoring_innings.append(inningnum)
                away_scoring_inning_plays[inningnum] = []
                runs_by_inning_away[inningnum] = [runs,[]]

        for play in self.home_play_by_play:
            inning = play.get('inning')
            if inning in home_scoring_innings:
                play_description = [play.get('batter_name'), play.get('des')]
                if len(home_scoring_inning_plays[inning]) == 0:
                    home_scoring_inning_plays[inning].append(play_description)
                elif len(home_scoring_inning_plays[inning]) > 0 and home_scoring_inning_plays[inning][-1] != play_description:
                    home_scoring_inning_plays[inning].append(play_description)


        for play in self.away_play_by_play:
            inning = play.get('inning')
            if inning in away_scoring_innings:
                play_description = [play.get('batter_name'), play.get('des')]

                if len(away_scoring_inning_plays[inning]) == 0:
                    away_scoring_inning_plays[inning].append(play_description)
                elif len(away_scoring_inning_plays[inning]) > 0 and away_scoring_inning_plays[inning][-1] != play_description:
                    away_scoring_inning_plays[inning].append(play_description)


    def findrunnersthatscore(self, aRBIdict, runs_remaining, runs_by_inning):

        for inning, plays_list in self.scoring_inning_plays.items():
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
                            print(player, players)
                            raise Exception("Player cannot have negative runs remaining")
            #print(batters_this_inning)
            print(inning,runs_by_inning[inning][1])
        for inning, plays_list in self.scoring_inning_plays.items():
            runners_that_score = runs_by_inning[inning][1]
            if len(runners_that_score) != runs_by_inning[inning][0]:
                runners_not_accounted_for = [player for player, runs in runs_remaining.items() if runs > 0]
                if len(runners_not_accounted_for) == 1:
                    player = runners_not_accounted_for[0]
                    runs_remaining[player] -= 1
                    runners_that_score.append(player)
                else:
                    raise Exception("ERROR: not all runners accounted for")
            self.calculateaRBI(runners_that_score, plays_list, aRBIdict)


    def calculateaRBI(self,runners_that_score, plays_list, aRBIdict):
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

        findrunnersthatscore(self.home_aRBI,runs_remaining_home, runs_by_inning_home)
        findrunnersthatscore(self.away_aRBI,runs_remaining_away, runs_by_inning_away)

# print(runs_by_inning_home)
# print(runs_by_inning_away)
homesum = 0
awaysum = 0
for players, aRBI in self.home_aRBI.items():
    if aRBI > 0:
        print(players,aRBI)
        homesum += aRBI

print("Home Total aRBI: ", homesum)

for players, aRBI in self.away_aRBI.items():
    if aRBI > 0:
        print(players, aRBI)
        awaysum += aRBI

print("Away Total aRBI: ", awaysum)