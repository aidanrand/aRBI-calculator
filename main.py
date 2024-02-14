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
            "https://baseballsavant.mlb.com/gf?game_pk=716803", "https://baseballsavant.mlb.com/gf?game_pk=716871","https://baseballsavant.mlb.com/gf?game_pk=717157"
            "https://baseballsavant.mlb.com/gf?game_pk=717038", "https://baseballsavant.mlb.com/gf?game_pk=717170"]
#links to check:
#https://baseballsavant.mlb.com/gamefeed?gamePk=717442
#https://baseballsavant.mlb.com/gamefeed?gamePk=717111
#https://baseballsavant.mlb.com/gamefeed?gamePk=717386
from game import Game
import game

start = time.time()

# for i in range(716404,718782):
# for i in range(717170,718782):
#     time.sleep(5)
#     print(i)
#     link = "https://baseballsavant.mlb.com/gf?game_pk=" + str(i)
# for i in range(1):
#     link = "https://baseballsavant.mlb.com/gf?game_pk=717386"
for link in links:
    newgame = Game(link)
    validlink = newgame.parse_json()
    if not validlink:
        print("INVALID GAME")
        continue
    game.get_lineup(newgame.home)
    game.get_lineup(newgame.away)
    newgame.get_scoring_innings()

    game.find_runners_that_score(newgame.home)
    game.find_runners_that_score(newgame.away)

    game.calculateaRBI(newgame.home)
    game.calculateaRBI(newgame.away)

    homesum = 0
    awaysum = 0
    for players, aRBI in newgame.home.aRBI.items():
        if aRBI > 0:
            #print(players, aRBI)
            homesum += aRBI

    #print("Home Total aRBI: ", homesum)

    for players, aRBI in newgame.away.aRBI.items():
        if aRBI > 0:
            #print(players, aRBI)
            awaysum += aRBI

    #print("Away Total aRBI: ", awaysum)

end = time.time()

print(end - start)