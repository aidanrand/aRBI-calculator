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
        #finding pinch runners
        positions = player_info.get('allPositions')
        if positions is None:
            continue
        for position in positions:
            if position.get('abbreviation') == 'PR':
                team.pinch_runners.append(player_name)


def get_play_by_play(team):
    for play in team.play_by_play:
        inning = play.get('inning')
        if inning in team.scoring_innings:
            play_description = [play.get('batter_name'), play.get('des'),play.get('result')]
            if len(team.scoring_inning_plays[inning]) == 0:
                team.scoring_inning_plays[inning].append(play_description)
            elif len(team.scoring_inning_plays[inning]) > 0 and team.scoring_inning_plays[inning][-1] != play_description:
                team.scoring_inning_plays[inning].append(play_description)

def reached_base_safely(result, play_description, batter):
    # the batter may have reached, another runner may have reached, or the batter may have been forced out
    if result == 'Forceout':
        regex = remove_accents(batter) + '[.]{0,4} out'
        finder = re.compile(regex)
        match = finder.findall(play_description)
        if len(match) > 0:
            return False
        return True

    safe = ['Single', 'Double', 'Triple', 'Home Run', 'Walk', 'Hit By Pitch', 'Field Error', 'Fielders Choice', 'Catcher Interference']
    out = ['Groundout', 'Flyout', 'Lineout', 'Pop Out', 'Strikeout', 'Double Play', 'Triple Play', 'GIDP', 'Sac Fly']
    if result in safe: return True
    if result in out: return False
    print(result)
    raise Exception("Invalid play result")

def runner_out_on_bases(runner, team, inning):
    for play in team.scoring_inning_plays[inning]:
        play_description = play[1]
        regex = remove_accents(runner) + '[.]{0,4} out'
        finder = re.compile(regex)
        match = finder.findall(play_description)
        if len(match) > 0:
            return True
    return False

# to track runners that scored but not accounted for in the play by play (e.g. wild pitch, passed ball, stolen base)
def adjust_for_uncounted_runners(team):
    runners_not_accounted_for = [player for player, runs in team.runs_remaining.items() if runs > 0]
    
    if len(runners_not_accounted_for) == 0:
        return
    
    if len(runners_not_accounted_for) == 1 and team.runs_remaining[runners_not_accounted_for[0]] == 1:
        print("FIRST")
        for inning in team.runs_by_inning.keys():
            if len(team.runs_by_inning[inning][1]) != team.runs_by_inning[inning][0]:
                runner = runners_not_accounted_for[0]
                team.runs_remaining[runner] -= 1
                team.runs_by_inning[inning][1].append(runner)
                runners_not_accounted_for = []
                return

    print("RUNNERS NOT ALL ACCOUNTED FOR: " , runners_not_accounted_for)
    #print(team.link)
    for inning in team.runs_by_inning.keys():        
        #all of the unaccounted for runners occured in the same inning
        if len(runners_not_accounted_for) + len(team.runs_by_inning[inning][1]) == team.runs_by_inning[inning][0]:
            print("SECOND")
            runners_accounted_for = []
            for runner in runners_not_accounted_for:
                team.runs_remaining[runner] -= 1
                team.runs_by_inning[inning][1].append(runner)
                runners_accounted_for.append(runner)

            runners_not_accounted_for = []
            return
    print("THIRD")
    #stores the innings in which an unaccounted for runner reached base (and their team scored that inning)
    scoring_innings_that_runners_are_not_accounted_for = {}
    for runner in runners_not_accounted_for:
        scoring_innings_that_runners_are_not_accounted_for[runner] = []
    unaccounted_for_innings = []
    innings_to_adjust = []

    for inning in team.scoring_inning_plays.keys():
        if len(team.runs_by_inning[inning][1]) != team.runs_by_inning[inning][0]:
            unaccounted_for_innings.append(inning)
        if len(team.runs_by_inning[inning][1]) == team.runs_by_inning[inning][0]:
            continue
        for play in team.scoring_inning_plays[inning]:
            batter = play[0]
            play_description = play[1]
            result = play[2]
            if batter in runners_not_accounted_for and reached_base_safely(result, play_description, batter) and not runner_out_on_bases(batter, team, inning):
                if batter in team.runs_by_inning[inning][1]:
                    continue

                scoring_innings_that_runners_are_not_accounted_for[batter].append(inning)
                innings_to_adjust.append(inning)

    innings_to_adjust.sort()
    unaccounted_for_innings.sort()
    if innings_to_adjust == unaccounted_for_innings:
        # for runners that are unnacounted for in only one scoring inning, we can assume they scored in that inning
        for runner, innings in scoring_innings_that_runners_are_not_accounted_for.items():
            if len(innings) == 1:
                inning = innings[0]
                team.runs_remaining[runner] -= 1
                team.runs_by_inning[inning][1].append(runner)
        runners_not_accounted_for = [player for player, runs in team.runs_remaining.items() if runs > 0]

    if len(runners_not_accounted_for) > 0:
        print("The following runners are not accounted for:")
        print(runners_not_accounted_for)
        print("Please enter the innings in which the following runners scored. Enter a number for an inning or 0 when finished.")
        for runner in runners_not_accounted_for:
            innings = []
            while True:
                user_input = input(f"Please enter an inning that {runner} scored: ")
                if user_input == "0":
                    break
                try:
                    user_input = int(user_input)
                except ValueError:
                    print("Invalid input. Please enter a number")
                    continue
                if user_input > 0 and user_input not in innings:
                    innings.append(user_input)
                else:
                    print("The number must be greater than or equal to zero and not previously inputted. Please try again.")

            for inning in innings:
                team.runs_remaining[runner] -= 1
                team.runs_by_inning[inning][1].append(runner)

def find_runners_that_score(team):
    for inning, plays_list in team.scoring_inning_plays.items():
        for play in plays_list:
            batter = play[0]
            play_description = play[1]
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
                runner_to_2nd_on_error_finder = re.compile(remove_accents(runner) + ' {0,4}advances to 2nd, on a.* error')
                match = runner_to_2nd_on_error_finder.findall(play_description)
                if len(match) == 0:
                    runner_to_2nd_finder = re.compile(remove_accents(runner) + ' {0,4}to 2nd')
                    match = runner_to_2nd_finder.findall(play_description)
                    if len(match) > 0:
                        aRBIs.append(runner)
                        team.aRBI[batter] += len(match)

                # batters where runners advance on an error are not given an aRBI
                runner_to_3rd_on_error_finder = re.compile(remove_accents(runner) + ' {0,4}advances to 3rd, on a.* error')
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

    #adjust_for_intentional_walks(team)

# to track runners that didn't bat due to being intentionally walked (no pitch data)
def adjust_for_intentional_walks(team):
    runners_that_did_not_bat_by_inning = {}
    players = team.players.keys()
    for inning, plays_list in team.scoring_inning_plays.items():
        batters = set()
        for play in plays_list:
            batters.add(play[0])
        for player in players:
            regex = remove_accents(player)
            finder = re.compile(regex)
            for play in plays_list:
                match = finder.findall(play[1])
                if len(match) > 0 and player not in batters and player not in team.pinch_runners:
                    if runners_that_did_not_bat_by_inning.get(inning) is None:
                        runners_that_did_not_bat_by_inning[inning] = [player]
                    elif player not in runners_that_did_not_bat_by_inning[inning]:
                        runners_that_did_not_bat_by_inning[inning].append(player)
        
        #removes automatic runner on second base in extra innings
        if inning > 9 and len(runners_that_did_not_bat_by_inning[inning]) == 1:
            runners_that_did_not_bat_by_inning.pop(inning)
            

    if len(runners_that_did_not_bat_by_inning) == 0:
        return
    
    for inning, runners in runners_that_did_not_bat_by_inning.items():
        for runner in runners:
            ordinal = convert_to_ordinal(inning)
            print(f"{runner} reached base in the {ordinal} inning but did not bat (likely due to an intentional walk)")
            while True:
                user_input = input(f"Please enter the number of aRBIs you would like to add to {runner}'s total: ")
                try:
                    user_input = int(user_input)
                except ValueError:
                    print("Invalid input. Please enter a number")
                    continue
                if user_input >= 0:
                    team.aRBI[runner] += user_input
                    break
                else:
                    print("The number must be greater than zero.")

def convert_to_ordinal(number):
    if 10 <= number % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
    return f"{number}{suffix}"
