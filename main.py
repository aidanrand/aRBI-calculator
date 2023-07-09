import json
import requests

link = "https://baseballsavant.mlb.com/gf?game_pk=717442"

json_data = requests.get(link).json()
keys = json_data.keys()

#playerIDs
away_lineup = json_data.get('away_lineup')
home_lineup = json_data.get('home_lineup')

game_date = json_data.get('gameDate')
scoreboard = json_data.get('scoreboard')
score_test = scoreboard.get('linescore')
home_team_data = json_data.get('home_team_data')
home_team = home_team_data.get('name')
away_team_data = json_data.get('away_team_data')
away_team = away_team_data.get('name')
away_batters = json_data.get('away_batters')
boxscore = json_data.get('boxscore')

print(score_test,'\n')
print(home_team_data, '\n')
print(away_batters, '\n\n')

print(boxscore)

#print(json_data.keys())

