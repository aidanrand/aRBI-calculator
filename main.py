import re
import requests
link = "https://baseballsavant.mlb.com/gf?game_pk=717111"
#link = "https://baseballsavant.mlb.com/gf?game_pk=663222"
#link = "https://baseballsavant.mlb.com/gf?game_pk=717404"
#link = "https://baseballsavant.mlb.com/gf?game_pk=717442"

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
away_aRBI = {}
for player_info in away_players_dict.values():
    player_id = player_info.get('person').get('id')
    player_name = player_info.get('person').get('fullName')
    away_players[player_name] = player_id
    away_aRBI[player_name] = 0

home_players_dict = boxscore_teams.get('home').get('players')
home_players = {}
home_aRBI = {}
for player_info in home_players_dict.values():
    player_id = player_info.get('person').get('id')
    player_name = player_info.get('person').get('fullName')
    home_players[player_name] = player_id
    home_aRBI[player_name] = 0

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

print(home_scoring_inning_plays)

print(away_scoring_inning_plays)
print(home_scoring_innings)
print(away_scoring_innings)

def calculateaRBI(scoring_inning_plays,aRBIdict,players):
    #calculate RBI and record runners that score
    for inning, plays_list in scoring_inning_plays.items():
        print(plays_list)
        runners_that_score = []
        for i in range(len(plays_list)-1,-1,-1):
            batter = plays_list[i][0]
            play_description = plays_list[i][1]
            for player in players.keys():
                runner_scored_re = player + '[ ]{0,4}scores'
                runner_finder = re.compile(runner_scored_re)
                match = runner_finder.findall(play_description)
                if len(match) > 0:
                    runners_that_score.append(player)
                    aRBIdict[batter] += len(match)
                homers_scored_re = player + '[ ]{0,4}homers'
                homer_finder = re.compile(homers_scored_re)
                match = homer_finder.findall(play_description)
                if len(match) > 0:
                    runners_that_score.append(player)
                    aRBIdict[batter] += len(match)
                grand_slam_scored_re = player + '.* grand slam'
                grand_slam_finder = re.compile(grand_slam_scored_re)
                match = grand_slam_finder.findall(play_description)
                if len(match) > 0:
                    runners_that_score.append(player)
                    aRBIdict[batter] += len(match)


calculateaRBI(home_scoring_inning_plays, home_aRBI, home_players)
calculateaRBI(away_scoring_inning_plays, away_aRBI, away_players)

homesum = 0
awaysum = 0
for players,aRBI in home_aRBI.items():
    if aRBI > 0:
        print(players,aRBI)
        homesum += aRBI

print("Total RBI: ",homesum)

for players,aRBI in away_aRBI.items():

    if aRBI > 0:
        print(players,aRBI)
        awaysum += aRBI

print("Total RBI: ",awaysum)




