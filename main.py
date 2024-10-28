import time
from game import Game
import game
import excel

# batter reaches on error: arbi
# runner scores on error (during an at bat e.g. wild pitch): no arbi
#runner that will score advances on error but does not score: no arbi
#batters who are pinch ran for do not recieve an arbi if their pinch runner scores

start = time.time()
# 2023 season: 716352 718782 (2429 total games)
# 2023 postseason: 748534 748585 (41 total games)
# All Star Game: 717421

count = 0
for i in range(748534,748586):
    link = "https://baseballsavant.mlb.com/gf?game_pk=" + str(i)

    newgame = Game(link)
    validlink = newgame.parse_json()
    if not validlink:
        print(link,"INVALID GAME")
        continue
    print(link)
    count += 1
    game.get_lineup(newgame.home)
    game.get_lineup(newgame.away)
    newgame.get_scoring_innings()

    game.find_runners_that_score(newgame.home)
    game.find_runners_that_score(newgame.away)

    game.calculateaRBI(newgame.home)
    game.calculateaRBI(newgame.away)
    
    filename = "aRBI2023.xlsx"
    data = {"month": newgame.month, "home": newgame.home.name, "home_players": 
            newgame.home.players, "home_aRBI": newgame.home.aRBI, 
            "away": newgame.away.name, "away_players": newgame.away.players,
            "away_aRBI": newgame.away.aRBI}
    
    excel.write_results_to_excel(data, filename, False)

end = time.time()

print(end - start)
print(count)