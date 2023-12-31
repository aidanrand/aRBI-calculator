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

    def parse_json(self):
        json_data = requests.get(self.link).json()
        #keys = json_data.keys()

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

    def get_scoring_innings(self):
        for inning in self.scoreboard_by_inning:
            runs = inning.get('home').get('runs')
            inningnum = inning.get('num')

            if runs is not None and runs > 0:
                self.home.scoring_innings.append(inningnum)
                self.home.scoring_inning_plays[inningnum] = []
                self.home.runs_by_inning[inningnum] = [runs, []]

            runs = inning.get('away').get('runs')
            if runs is not None and runs > 0:
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

    def findrunnersthatscore(self, team):
        for inning, plays_list in team.scoring_inning_plays.items():

            #batters_this_inning = []
            for i in range(len(plays_list)):
                batter = plays_list[i][0]
                #batters_this_inning.append(batter)
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
        runners_not_accounted_for = [player for player, runs in team.runs_remaining.items() if runs > 0]
        for inning, plays_list in team.scoring_inning_plays.items():
            #team.runners_that_score[inning] = team.runs_by_inning[inning][1]
            if len(team.runs_by_inning[inning][1]) != team.runs_by_inning[inning][0]:
                if len(runners_not_accounted_for) == 1:
                    runner = runners_not_accounted_for[0]
                    team.runs_remaining[runner] -= 1
                    team.runs_by_inning[inning][1].append(runner)
                    runners_not_accounted_for.remove(runner)
                    break
                elif len(runners_not_accounted_for) + len(team.runs_by_inning[inning][1]) == team.runs_by_inning[inning][0]:
                    print("here")
                    for runner in runners_not_accounted_for:
                        team.runs_remaining[runner] -= 1
                        team.runs_by_inning[inning][1].append(runner)
                        runners_not_accounted_for.remove(runner)
                    break
                else:
                    print("here2")
                    self.find_runners_not_in_play_description(team,inning, runners_not_accounted_for)
        if len(runners_not_accounted_for) > 0:
            print(team.scoring_inning_plays)
            print(runners_not_accounted_for)
            raise Exception("ERROR: not all runners accounted for")

    def find_runners_not_in_play_description(self, team, inning, runners_not_accounted_for):
        for runner in runners_not_accounted_for:
            run_finder = re.compile(runner + '[ ]{0,4}scores')
            matches = []
            for play in team.scoring_inning_plays[inning]:
                play_description = play[1]
                matches += run_finder.findall(play_description)
            if len(matches) > 0:
                continue

            runner_on_3rd_finder = re.compile(runner + ' {0,4}to 3rd')
            for play in team.scoring_inning_plays[inning]:
                play_description = play[1]
                match = runner_on_3rd_finder.findall(play_description)
                if len(match) > 0:
                    team.runs_by_inning[inning][1].append(runner)
                    team.runs_remaining[runner] -= 1
                    runners_not_accounted_for.remove(runner)
                    if team.runs_remaining[runner] < 0:
                        print(runner, team.runs_remaining)
                        print(team.scoring_inning_plays[inning])
                        raise Exception("Player cannot have negative runs remaining")

                    break


    def calculateaRBI(self, team):
        for inning,plays_list in team.scoring_inning_plays.items():
            for i in range(len(plays_list)-1,-1,-1):
                batter = plays_list[i][0]
                play_description = plays_list[i][1]
                aRBIs = []
                for runner in set(team.runs_by_inning[inning][1]):
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
                if aRBIs.count(runner) > team.runs_by_inning[inning][1].count(runner):
                    print(aRBIs)
                    print(team.runs_by_inning[inning][1])
                    raise Exception("Overcounted a runner")

        for inning, runners in team.runs_by_inning.items():
            for runner in runners[1]:
                team.aRBI[runner] += 1

