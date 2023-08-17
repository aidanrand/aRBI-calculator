import re
import requests
#link = "https://baseballsavant.mlb.com/gf?game_pk=717111"
#link = "https://baseballsavant.mlb.com/gf?game_pk=663222"
#link = "https://baseballsavant.mlb.com/gf?game_pk=717311"
link = "https://baseballsavant.mlb.com/gf?game_pk=717222"
#link = "https://baseballsavant.mlb.com/gf?game_pk=717404"
#link = "https://baseballsavant.mlb.com/gf?game_pk=717442"

#To do: find a game with a wild pitch with runner that scores, steal of 2nd, and reach on error, player that scores twice in an inning
# batter reaches on error: no arbi
# runner scores on error: no arbi
#runner that will score advances on error but does not score: arbi
#batters who are pinch ran for do not recieve an arbi if their pinch runner scores
json_data = requests.get(link).json()
keys = json_data.keys()

# away_lineup = json_data.get('away_lineup')
# home_lineup = json_data.get('home_lineup')

game_date = json_data.get('gameDate')
scoreboard = json_data.get('scoreboard')
scoreboard_by_inning = scoreboard.get('linescore').get('innings')

home_team_data = json_data.get('home_team_data')
home_team = home_team_data.get('name')
#home_abbreviation = home_team_data.get('abbreviation')
#data for team is listed when they are pitching, not when they are batting
home_team_play_by_play = json_data.get('team_away')

away_team_data = json_data.get('away_team_data')
away_team = away_team_data.get('name')
#away_abbreviation = away_team_data.get('abbreviation')
away_team_play_by_play = json_data.get('team_home')

away_batters = json_data.get('away_batters')
boxscore = json_data.get('boxscore')
boxscore_teams = boxscore.get('teams')

away_players = {}
away_aRBI = {}
runs_remaining_away = {}
for player_info in boxscore_teams.get('away').get('players').values():
    player_id = player_info.get('person').get('id')
    player_name = player_info.get('person').get('fullName')
    player_runs = player_info.get('stats').get('batting').get('runs')
    if player_runs is None:
        player_runs = 0
    runs_remaining_away[player_name] = player_runs
    away_players[player_name] = player_id
    away_aRBI[player_name] = 0

home_players = {}
home_aRBI = {}
runs_remaining_home = {}
for player_info in  boxscore_teams.get('home').get('players').values():
    player_id = player_info.get('person').get('id')
    player_name = player_info.get('person').get('fullName')
    player_runs = player_info.get('stats').get('batting').get('runs')
    if player_runs is None:
        player_runs = 0
    runs_remaining_home[player_name] = player_runs
    home_players[player_name] = player_id
    home_aRBI[player_name] = 0

#away_team_runs_by_inning = ['Away: ']
away_scoring_innings = []
away_scoring_inning_plays = {}
runs_by_inning_away = {}

#home_team_runs_by_inning = ['Home: ']
home_scoring_innings = []
home_scoring_inning_plays = {}
runs_by_inning_home = {}

for inning in scoreboard_by_inning:
    runs = inning.get('home').get('runs')
    inningnum = inning.get('num')
    # no runs if bottom of ninth isn't played
    if runs is None:
        continue
        #home_team_runs_by_inning.append('X')
    else:
        #home_team_runs_by_inning.append(runs)
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

for play in home_team_play_by_play:
    inning = play.get('inning')
    if inning in home_scoring_innings:
        play_description = [play.get('batter_name'), play.get('des')]
        if len(home_scoring_inning_plays[inning]) == 0:
            home_scoring_inning_plays[inning].append(play_description)
        elif len(home_scoring_inning_plays[inning]) > 0 and home_scoring_inning_plays[inning][-1] != play_description:
            home_scoring_inning_plays[inning].append(play_description)

for play in away_team_play_by_play:
    inning = play.get('inning')
    if inning in away_scoring_innings:
        play_description = [play.get('batter_name'), play.get('des')]
        if len(away_scoring_inning_plays[inning]) == 0:
            away_scoring_inning_plays[inning].append(play_description)
        elif len(away_scoring_inning_plays[inning]) > 0 and away_scoring_inning_plays[inning][-1] != play_description:
            away_scoring_inning_plays[inning].append(play_description)


def findrunnersthatscore(scoring_inning_plays, aRBIdict, runs_remaining, runs_by_inning):

    for inning, plays_list in scoring_inning_plays.items():
        batters_this_inning = []
        for i in range(len(plays_list)-1,-1,-1):
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
                    if runs_remaining[player] < 0 :
                        print(player,runs_remaining)
                        raise Exception("Player cannot have negative runs remaining")

                homers_scored_re = player + '[ ]{0,4}homers'
                homer_finder = re.compile(homers_scored_re)
                match = homer_finder.findall(play_description)
                if len(match) > 0:
                    runs_by_inning[inning][1].append(player)
                    aRBIdict[batter] += len(match)
                    runs_remaining[player] -= 1
                    if runs_remaining[player] < 0:
                        print(player, runs_remaining)
                        raise Exception("Player cannot have negative runs remaining")

                grand_slam_scored_re = player + '.* grand slam'
                grand_slam_finder = re.compile(grand_slam_scored_re)
                match = grand_slam_finder.findall(play_description)
                if len(match) > 0:
                    runs_by_inning[inning][1].append(player)
                    aRBIdict[batter] += len(match)
                    runs_remaining[player] -= 1
                    if players[player][1] < 0:
                        print(player, players)
                        raise Exception("Player cannot have negative runs remaining")

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
        calculateaRBI(runners_that_score, plays_list, aRBIdict)


def calculateaRBI(runners_that_score, plays_list, aRBIdict):
    for i in range(len(plays_list)-1,-1,-1):
        batter = plays_list[i][0]
        play_description = plays_list[i][1]
        # if batter in runners_that_score:
        #     continue
        #     #runners_that_score.remove(batter)

        for runner in runners_that_score:
            #batters where runners advance on an error are not given an aRBI
            runner_to_2nd_on_error_finder = re.compile(runner + '\\.* to 2nd' + '\\.* error')
            match = runner_to_2nd_on_error_finder.findall(play_description)

            if len(match) == 0:
                runner_to_2nd_finder = re.compile(runner + '[ ]{0,4}to 2nd')
                match = runner_to_2nd_finder.findall(play_description)
                if len(match) > 0:
                    aRBIdict[batter] += len(match)

            # batters where runners advance on an error are not given an aRBI
            runner_to_3rd_on_error_finder = re.compile(runner + '\\.* to 3rd' + '\\.* error')
            match = runner_to_3rd_on_error_finder.findall(play_description)
            if len(match) == 0:
                runner_to_3rd_finder = re.compile(runner + '[ ]{0,4}to 3rd')
                match = runner_to_3rd_finder.findall(play_description)
                if len(match) > 0:
                    aRBIdict[batter] += len(match)

            single_finder = re.compile(runner + '[ ]{0,4}singles')
            match = single_finder.findall(play_description)
            if len(match) > 0:
                aRBIdict[batter] += len(match)

            double_finder = re.compile(runner + '[ ]{0,4}doubles')
            match = double_finder.findall(play_description)
            if len(match) > 0:
                aRBIdict[batter] += len(match)

            triple_finder = re.compile(runner + '[ ]{0,4}triples')
            match = triple_finder.findall(play_description)
            if len(match) > 0:
                aRBIdict[batter] += len(match)

            walk_finder = re.compile(runner + '[ ]{0,4}walks')
            match = walk_finder.findall(play_description)
            if len(match) > 0:
                aRBIdict[batter] += len(match)

            fielders_choice_finder = re.compile(runner + '[ ]{0,4}reaches on a fielder\'s choice')
            match = fielders_choice_finder.findall(play_description)
            if len(match) > 0:
                aRBIdict[batter] += len(match)

            hit_by_pitch_finder = re.compile(runner + '[ ]{0,4}hit by pitch')
            match = hit_by_pitch_finder.findall(play_description)
            if len(match) > 0:
                aRBIdict[batter] += len(match)


findrunnersthatscore(home_scoring_inning_plays, home_aRBI, runs_remaining_home, runs_by_inning_home)
findrunnersthatscore(away_scoring_inning_plays, away_aRBI, runs_remaining_away, runs_by_inning_away)

print(runs_by_inning_home)
print(runs_by_inning_away)
homesum = 0
awaysum = 0
for players, aRBI in home_aRBI.items():
    if aRBI > 0:
        print(players,aRBI)
        homesum += aRBI

print("Total aRBI: ", homesum)

for players, aRBI in away_aRBI.items():
    if aRBI > 0:
        print(players, aRBI)
        awaysum += aRBI

print("Total aRBI: ", awaysum)
