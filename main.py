# import re
# import requests
import time
#link = "https://baseballsavant.mlb.com/gf?game_pk=717111" #correct (1,34)

#link = "https://baseballsavant.mlb.com/gf?game_pk=663222" #correct (6,66)
#link = "https://baseballsavant.mlb.com/gf?game_pk=717311" #correct (9,3)
#link = "https://baseballsavant.mlb.com/gf?game_pk=717222" #correct (9,3)
#link = "https://baseballsavant.mlb.com/gf?game_pk=717404" #correct (9,5)
#link = "https://baseballsavant.mlb.com/gf?game_pk=717442" #correct (4,0)

links = ["https://baseballsavant.mlb.com/gf?game_pk=717111", "https://baseballsavant.mlb.com/gf?game_pk=663222", "https://baseballsavant.mlb.com/gf?game_pk=717311",
         "https://baseballsavant.mlb.com/gf?game_pk=717222", "https://baseballsavant.mlb.com/gf?game_pk=717404", "https://baseballsavant.mlb.com/gf?game_pk=717442"]
#Done: find a game with a wild pitch with runner that scores, steal of 2nd, and reach on error
# batter reaches on error: no arbi
# runner scores on error: no arbi
#runner that will score advances on error but does not score: arbi
#batters who are pinch ran for do not recieve an arbi if their pinch runner scores
newlinks = ["https://baseballsavant.mlb.com/gf?game_pk=716484", "https://baseballsavant.mlb.com/gf?game_pk=716492","https://baseballsavant.mlb.com/gf?game_pk=716630",
            "https://baseballsavant.mlb.com/gf?game_pk=717404"]
from game import Game
start = time.time()
for i in range(716404,718782):
    print(i)
    link = "https://baseballsavant.mlb.com/gf?game_pk=" + str(i)
    newgame = Game(link)
    newgame.parse_json()
    newgame.get_lineup(newgame.home)
    newgame.get_lineup(newgame.away)
    newgame.get_scoring_innings()

    newgame.findrunnersthatscore(newgame.home)
    newgame.findrunnersthatscore(newgame.away)

    newgame.calculateaRBI(newgame.home)
    newgame.calculateaRBI(newgame.away)

    homesum = 0
    awaysum = 0
    for players, aRBI in newgame.home.aRBI.items():
        if aRBI > 0:
            #print(players, aRBI)
            homesum += aRBI

    print("Home Total aRBI: ", homesum)

    for players, aRBI in newgame.away.aRBI.items():
        if aRBI > 0:
            #print(players, aRBI)
            awaysum += aRBI

    print("Away Total aRBI: ", awaysum)

end = time.time()

print(end - start)