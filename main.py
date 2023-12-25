import re
import requests
#link = "https://baseballsavant.mlb.com/gf?game_pk=717111" #correct

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

