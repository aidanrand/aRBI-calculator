import time
from game import Game
import game
# batter reaches on error: arbi
# runner scores on error (during an at bat e.g. wild pitch): no arbi
#runner that will score advances on error but does not score: no arbi
#batters who are pinch ran for do not recieve an arbi if their pinch runner scores

#check inside the park home run
# check intentional walk


start = time.time()

# for i in range(716404,718782):
# for i in range(717170,718782):
#     time.sleep(5)
#     print(i)

for i in range(1):

    #link = "https://baseballsavant.mlb.com/gf?game_pk=662014"
    link = "https://baseballsavant.mlb.com/gf?game_pk=717311"
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
            print(players, aRBI)
            homesum += aRBI

    print("Home Total aRBI: ", homesum)

    for players, aRBI in newgame.away.aRBI.items():
        if aRBI > 0:
            print(players, aRBI)
            awaysum += aRBI

    print("Away Total aRBI: ", awaysum)

end = time.time()

print(end - start)