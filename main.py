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
#data for team is listed when they are pitching, not when they are batting
home_team_play_by_play = json_data.get('team_away')

away_team_data = json_data.get('away_team_data')
away_team = away_team_data.get('name')
away_abbreviation = away_team_data.get('abbreviation')
away_team_play_by_play = json_data.get('team_home')

away_batters = json_data.get('away_batters')
boxscore = json_data.get('boxscore')
boxscore_teams = boxscore.get('teams')
away_players_dict = boxscore_teams.get('away').get('players')
away_players = {}
for player_info in away_players_dict.values():
    player_id = player_info.get('person').get('id')
    player_name = player_info.get('person').get('fullName')
    away_players[player_name] = player_id

home_players_dict = boxscore_teams.get('home').get('players')
home_players = {}
for player_info in home_players_dict.values():
    player_id = player_info.get('person').get('id')
    player_name = player_info.get('person').get('fullName')
    home_players[player_name] = player_id

print(away_players)
print(home_players)

#To Do:
#print(json_data.get('team_home'),'\n')


away_team_runs_by_inning = ['Away: ']
away_scoring_innings = []
away_scoring_inning_plays = {}
away_team_runs = {}

home_team_runs_by_inning = ['Home: ']
home_scoring_innings = []
home_scoring_inning_plays = {}
home_team_runs = {}

for inning in scoreboard_by_inning:
    runs = inning.get('home').get('runs')
    inningnum = inning.get('num')
    # no runs if bottom of ninth isn't played
    if runs is None:
        home_team_runs_by_inning.append('X')
    else:
        home_team_runs_by_inning.append(runs)
        if runs > 0:
            home_scoring_innings.append(inningnum)
            home_scoring_inning_plays[inningnum] = []
            home_team_runs[inningnum] = []

    runs = inning.get('away').get('runs')
    away_team_runs_by_inning.append(runs)
    if runs > 0:
        away_scoring_innings.append(inningnum)
        away_scoring_inning_plays[inningnum] = []
        away_team_runs[inningnum] = []

print(home_scoring_inning_plays)
print(away_scoring_inning_plays)
for play in home_team_play_by_play:
    inning = play.get('inning')
    if inning in home_scoring_innings:
        play_description = [play.get('batter_name'), play.get('des')]
        print(play_description)
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
        elif len(away_scoring_inning_plays[inning]) > 0 and away_scoring_inning_plays[-1] != play_description:
            away_scoring_inning_plays[inning].append(play_description)

print(home_scoring_inning_plays)

print(away_scoring_inning_plays)

# print(home_team_play_by_play)