#     data.py    #
# Written By GQX #

ASSETDIR   = __file__[:-7] + "assets/"
TMPDIR     = "/tmp/py2048/"

# Socket
PORT       = 50000
TIMEOUT    = 2

# Colors
DARKMODE   = False
BLACK      = (0  , 0  , 0  )
WHITE      = (255, 255, 255)
ORANGE     = (255, 125, 64 )
RED        = (255, 0  , 0  )
BLACKGREY  = (50 , 50 , 50 )
#COLORS = (
#    (0  , 0  , 0  ),
#    (0  , 0  , 50 ),
#    (0  , 0  , 100)
#)

if DARKMODE:
    BLACK, WHITE = WHITE, BLACK

# Sounds
BGM        = ASSETDIR + "Nevada.mp3"

# Pictures
PICTURES   = [ASSETDIR + l + ".png" for l in ("P2","P4","P8","P16","P32","P64","P128","P256","P512","P1024","P2048")]

# Fonts
FONTPATH   = ASSETDIR + "SourceCodePro.ttf"

# Directions
LEFT       = "left"
RIGHT      = "right"
UP         = "up"
DOWN       = "down"
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

# Actions
FREEZE     = "freeze"
MOVE       = "move"
MERGE      = "merge"

# data
DATADIR = __file__[:-7] + "data/"
SCORELIST = DATADIR + "ScoreList.json"