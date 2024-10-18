import re
import unicodedata
import requests
from team import Team


class Game:
    def __init__(self, link):
        self.link = link
        self.game_date = None
        self.scoreboard_by_inning = None
        self.home = Team()
        self.away = Team()
        self.home.link = link
        self.away.link = link

    def parse_json(self):
        json_data = requests.get(self.link).json()
        if json_data.get("error") == "Invalid Game PK.":
            return False
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
        return True

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
        
        get_play_by_play(self.home)
        get_play_by_play(self.away)


def get_lineup(team):
    for player_info in team.players_info:
        player_id = player_info.get('person').get('id')
        player_name = player_info.get('person').get('fullName')
        player_runs = player_info.get('stats').get('batting').get('runs')
        if player_runs is None:
            player_runs = 0
        team.runs_remaining[player_name] = player_runs
        team.players[player_name] = player_id
        team.aRBI[player_name] = 0


def get_play_by_play(team):
    for play in team.play_by_play:
        inning = play.get('inning')
        if inning in team.scoring_innings:
            play_description = [play.get('batter_name'), play.get('des'),play.get('result')]
            if len(team.scoring_inning_plays[inning]) == 0:
                team.scoring_inning_plays[inning].append(play_description)
            elif len(team.scoring_inning_plays[inning]) > 0 and team.scoring_inning_plays[inning][-1] != play_description:
                team.scoring_inning_plays[inning].append(play_description)


# def find_runners_not_in_play_description(team, inning, runners_not_accounted_for):
#     print("Wack")
#     for runner in runners_not_accounted_for:
#         run_finder = re.compile(remove_accents(runner) + '[ ]{0,4}scores')
#         matches = []
#         for play in team.scoring_inning_plays[inning]:
#             play_description = play[1]
#             matches += run_finder.findall(play_description)
#         if len(matches) > 0:
#             continue

#         runner_on_3rd_finder = re.compile(remove_accents(runner) + ' {0,4}to 3rd')
#         for play in team.scoring_inning_plays[inning]:
#             play_description = play[1]
#             match = runner_on_3rd_finder.findall(play_description)
#             if len(match) > 0:
#                 team.runs_by_inning[inning][1].append(runner)
#                 team.runs_remaining[runner] -= 1
#                 runners_not_accounted_for.remove(runner)
#                 if team.runs_remaining[runner] < 0:
#                     print(runner, team.runs_remaining)
#                     print(team.scoring_inning_plays[inning])
#                     raise Exception("Player cannot have negative runs remaining")

#                 break

def reached_base_safely(result):
    safe = ['Single', 'Double', 'Triple', 'Home Run', 'Walk', 'Hit By Pitch', 'Field Error', 'Fielders Choice', 'Catcher Interference']
    out = ['Groundout', 'Flyout', 'Lineout', 'Pop Out', 'Strikeout', 'Double Play', 'Triple Play', 'Forceout']
    if result in safe: return True
    if result in out: return False
    print(result)
    raise Exception("Invalid play result")

def adjust_for_uncounted_runners(team):
    runners_not_accounted_for = [player for player, runs in team.runs_remaining.items() if runs > 0]
    
    print(runners_not_accounted_for)
    if len(runners_not_accounted_for) == 0:
        return
    
    print("RUNNERS NOT ALL ACCOUNTED FOR")
    print(team.link)
    if len(runners_not_accounted_for) == 1:
        for inning in team.runs_by_inning.keys():
            if len(team.runs_by_inning[inning][1]) != team.runs_by_inning[inning][0]:
                runner = runners_not_accounted_for[0]
                team.runs_remaining[runner] -= 1
                team.runs_by_inning[inning][1].append(runner)
                runners_not_accounted_for = []
                return

    for inning in team.runs_by_inning.keys():        
        #all of the unaccounted for runners occured in the same inning
        if len(runners_not_accounted_for) + len(team.runs_by_inning[inning][1]) == team.runs_by_inning[inning][0]:
            print("here")
            runners_accounted_for = []
            for runner in runners_not_accounted_for:
                team.runs_remaining[runner] -= 1
                team.runs_by_inning[inning][1].append(runner)
                runners_accounted_for.append(runner)

            runners_not_accounted_for = []
            return
    
    #stores the innings in which an unaccounted for runner reached base (and their team scored that inning)
    scoring_innings_that_runners_are_not_accounted_for = {}
    for runner in runners_not_accounted_for:
        scoring_innings_that_runners_are_not_accounted_for[runner] = []

    for inning in team.scoring_inning_plays.keys():
        for play in team.scoring_inning_plays[inning]:
            batter = play[0]
            result = play[2]
            reached_base_safely(result)
            if batter in runners_not_accounted_for and reached_base_safely(result):
                scoring_innings_that_runners_are_not_accounted_for[batter].append(inning)

    # for runners that are unnacounted for in only one scoring inning, we can assume they scored in that inning

    for runner, innings in scoring_innings_that_runners_are_not_accounted_for.items():
        if len(innings) == 1:
            team.runs_remaining[runner] -= 1
            team.runs_by_inning[inning][1].append(runner)
    
    runners_not_accounted_for = [player for player, runs in team.runs_remaining.items() if runs > 0]

    if len(runners_not_accounted_for) > 0:
        print("The following runners are not accounted for:")
        print(runners_not_accounted_for)
        print("Please enter the innings in which the following runners scored. Enter a number for an inning or 'DONE' when finished.")
        for runner in runners_not_accounted_for:
            innings = []
            while True:
                try:
                    user_input = int(input("Please enter an inning that {runner} scored: "))
                    if user_input == "DONE":
                        break
                    if user_input > 0 and user_input not in innings:
                        innings.append(user_input)
                    else:
                        print("The number must be greater than zero. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a valid inning.")

            for inning in innings:
                team.runs_remaining[runner] -= 1
                team.runs_by_inning[inning][1].append(runner)

                # batters.append(play[0])
    # print(team.runs_by_inning[inning])
    # print("here2")
    # # check to see if the runners 
    # print(team.runs_by_inning[inning][0])
    # print(team.runs_by_inning[inning][1])
    # batters = []
    # for play in team.scoring_inning_plays[inning]:
    #     if play[0] in runners_not_accounted_for.keys():
    #         batters.append(play[0])
    #     print(play)
    # print(batters)

            # find_runners_not_in_play_description(team, inning, runners_not_accounted_for)
            # if len(runners_not_accounted_for) == 1:
            #     runner = runners_not_accounted_for[0]
            #     team.runs_remaining[runner] -= 1
            #     team.runs_by_inning[inning][1].append(runner)
            #     runners_not_accounted_for.remove(runner)
            #     break
    # if len(runners_not_accounted_for) > 0:
    #     return
    #     print(runners_not_accounted_for)
    #     print(team.scoring_inning_plays)
    #     print(runners_not_accounted_for)
    #     raise Exception("ERROR: not all runners accounted for")


def find_runners_that_score(team):
    for inning, plays_list in team.scoring_inning_plays.items():
        for i in range(len(plays_list)):
            #print(plays_list[i][2])
            batter = plays_list[i][0]
            play_description = plays_list[i][1]
            for player in team.runs_remaining.keys():
                if team.runs_remaining[player] == 0:
                    continue
                re_finder(player, batter, inning, plays_list, play_description, '[ ]{0,4}scores', team, home_run = False)
                re_finder(player, batter, inning, plays_list, play_description, '[ ]{0,4}homers', team, home_run = True)
                re_finder(player, batter, inning, plays_list, play_description, '.* grand slam', team, home_run = True)

    adjust_for_uncounted_runners(team)

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def re_finder(player, batter, inning, plays_list, play_description, expression, team, home_run):
    regex = remove_accents(player) + expression
    finder = re.compile(regex)
    match = finder.findall(play_description)
    #if inning ==  6 and player == 'Christian Vázquez':
        # print(match)
        # print("IOUGSHRIGWUR")
        # print(play_description)
    if len(match) > 0:
        team.runs_by_inning[inning][1].append(player)
        #to avoid double counting homeruns
        if not home_run:
            team.aRBI[batter] += len(match)
        team.runs_remaining[player] -= 1
        if team.runs_remaining[player] < 0:
            print(player,team.runs_remaining)
            print(plays_list)
            raise Exception("Player cannot have negative runs remaining")
        
def calculateaRBI(team):
    for inning,plays_list in team.scoring_inning_plays.items():
        for i in range(len(plays_list)-1,-1,-1):
            batter = plays_list[i][0]
            play_description = plays_list[i][1]
            play_result = plays_list[i][2]
            aRBIs = []
            for runner in set(team.runs_by_inning[inning][1]):
                if runner == batter:
                    continue
                # batters where runners advance on an error are not given an aRBI
                runner_to_2nd_on_error_finder = re.compile(remove_accents(runner) + '.* to 2nd.* error')
                match = runner_to_2nd_on_error_finder.findall(play_description)
                if len(match) == 0:
                    runner_to_2nd_finder = re.compile(remove_accents(runner) + ' {0,4}to 2nd')
                    match = runner_to_2nd_finder.findall(play_description)
                    if len(match) > 0:
                        aRBIs.append(runner)
                        team.aRBI[batter] += len(match)

                # batters where runners advance on an error are not given an aRBI
                runner_to_3rd_on_error_finder = re.compile(remove_accents(runner) + '.* to 3rd.* error')
                match = runner_to_3rd_on_error_finder.findall(play_description)
                if len(match) == 0:
                    runner_to_3rd_finder = re.compile(remove_accents(runner) + ' {0,4}to 3rd')
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



