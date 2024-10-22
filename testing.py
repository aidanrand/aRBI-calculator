from game import Game
import game
import time

start = time.time()

links = [                            #link to game, correct home aRBI, correct away aRBI
    ["https://baseballsavant.mlb.com/gf?game_pk=717111", 1, 34], #correct (1,34)
    ["https://baseballsavant.mlb.com/gf?game_pk=663222", 6, 66], #correct (6,66)
    ["https://baseballsavant.mlb.com/gf?game_pk=717311", 9, 3], #correct (9,3)
    ["https://baseballsavant.mlb.com/gf?game_pk=717222", 9, 3], #correct (9,3)
    ["https://baseballsavant.mlb.com/gf?game_pk=717404", 10, 5], #correct (10,5)
    ["https://baseballsavant.mlb.com/gf?game_pk=717442", 4, 0], #correct (4,0)
    ["https://baseballsavant.mlb.com/gf?game_pk=716484", 15, 5], #correct (15,5)
    ["https://baseballsavant.mlb.com/gf?game_pk=716492", 10, 10], #correct (10,10)
    ["https://baseballsavant.mlb.com/gf?game_pk=716630", 11, 23], #correct (11,23)
    ["https://baseballsavant.mlb.com/gf?game_pk=716803", 11, 2],  #correct (11,2)
    ["https://baseballsavant.mlb.com/gf?game_pk=716871", 5, 24], #correct (5,24)
    ["https://baseballsavant.mlb.com/gf?game_pk=717157", 14, 3], #correct (14,3)
    ["https://baseballsavant.mlb.com/gf?game_pk=717038", 22, 18], #correct (22,18)
    ["https://baseballsavant.mlb.com/gf?game_pk=717170", 17, 15], #correct (17,15) need user input
    ["https://baseballsavant.mlb.com/gf?game_pk=717386", 18, 11], #correct (18,11)
    ["https://baseballsavant.mlb.com/gf?game_pk=662014", 17, 14], #correct (17,14) need user input
]


# for i in range(716404,718782):
# for i in range(717170,718782):
for i in range(len(links)):
    link = links[i][0]
    #print(link)
    correcthome = links[i][1]
    correctaway = links[i][2]
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

    for players, aRBI in newgame.away.aRBI.items():
        if aRBI > 0:
            #print(players, aRBI)
            awaysum += aRBI

    if homesum == correcthome and awaysum == correctaway:
        print(link, "....Correct")
    else:
        print(link, "....Incorrect")
        if homesum != correcthome:
            for players, aRBI in newgame.home.aRBI.items():
                if aRBI > 0:
                    print(players, aRBI)
            print("Correct Home: ", correcthome)
            print("Home Total aRBI: ", homesum)
        if awaysum != correctaway:
            for players, aRBI in newgame.away.aRBI.items():
                if aRBI > 0:
                    print(players, aRBI)
            print("Correct Away: ", correctaway)
            print("Away Total aRBI: ", awaysum)

        print("\n")

end = time.time()

print(end - start)
