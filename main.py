import re
import requests
link = "https://baseballsavant.mlb.com/gf?game_pk=717111" #correct

#link = "https://baseballsavant.mlb.com/gf?game_pk=663222" #correct
#link = "https://baseballsavant.mlb.com/gf?game_pk=717311" #correct
#link = "https://baseballsavant.mlb.com/gf?game_pk=717222" #correct
#link = "https://baseballsavant.mlb.com/gf?game_pk=717404" #correct
#link = "https://baseballsavant.mlb.com/gf?game_pk=717442" #correct

#Done: find a game with a wild pitch with runner that scores, steal of 2nd, and reach on error
# batter reaches on error: no arbi
# runner scores on error: no arbi
#runner that will score advances on error but does not score: arbi
#batters who are pinch ran for do not recieve an arbi if their pinch runner scores
from game import game

newgame = game(link)
newgame.findrunnersthatscore(newgame.home_aRBI, runs_remaining_home, runs_by_inning_home)
newgame.findrunnersthatscore(self.away_aRBI, runs_remaining_away, runs_by_inning_away)

# print(runs_by_inning_home)
# print(runs_by_inning_away)
homesum = 0
awaysum = 0
for players, aRBI in self.home_aRBI.items():
    if aRBI > 0:
        print(players, aRBI)
        homesum += aRBI

print("Home Total aRBI: ", homesum)

for players, aRBI in self.away_aRBI.items():
    if aRBI > 0:
        print(players, aRBI)
        awaysum += aRBI

print("Away Total aRBI: ", awaysum)