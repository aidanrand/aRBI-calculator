import json
import requests

link = "https://baseballsavant.mlb.com/gf?game_pk=717442"

json_data = requests.get(link).json()
keys = json_data.keys()

#playerIDs may not need
away_lineup = json_data.get('away_lineup')
home_lineup = json_data.get('home_lineup')

game_date = json_data.get('gameDate')
scoreboard = json_data.get('scoreboard')
scoreboard_by_inning = scoreboard.get('linescore').get('innings')

home_team_data = json_data.get('home_team_data')
home_team = home_team_data.get('name')
home_abbreviation = home_team_data.get('abbreviation')
home_team_play_by_play = json_data.get('team_home')


away_team_data = json_data.get('away_team_data')
away_team = away_team_data.get('name')
away_abbreviation = away_team_data.get('abbreviation')
away_team_play_by_play = json_data.get('team_away')

away_batters = json_data.get('away_batters')
boxscore = json_data.get('boxscore')
boxscore_teams = boxscore.get('teams')
print(boxscore_teams)
print(boxscore.keys(),'\n')

print(json_data.keys(),'\n')
#yes this is it
#print(json_data.get('team_home'),'\n')


away_team_runs_by_inning = ['Away: ']
away_scoring_innings = []
home_team_runs_by_inning = ['Home: ']
home_scoring_innings = []
print(scoreboard_by_inning)
# for each in scoreboard_by_inning:
#     runs = each.get('home')
#         #.get('runs')
#     print(runs)
#     home_team_runs_by_inning.append(runs)
    # if runs > 0:
    #     home_scoring_innings.append(each.get('num'))
    # runs = each.get('away').get('runs')
    # away_team_runs_by_inning.append(runs)
    # if runs > 0:
    #     away_scoring_innings.append(each.get('num'))

print(home_team_runs_by_inning)
print(home_scoring_innings)
print(away_team_runs_by_inning)
print(away_scoring_innings)