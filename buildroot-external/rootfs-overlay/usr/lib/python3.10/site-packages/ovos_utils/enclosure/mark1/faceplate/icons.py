from ovos_utils.enclosure.mark1.faceplate import FaceplateGrid, BlackScreen


# drawing in python


class MusicIcon(BlackScreen):
    str_grid = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXX     XXXXXXXXXXXXX
XXXXXXXXXXXXXX     XXXXXXXXXXXXX
XXXXXXXXXXXXXX XXX XXXXXXXXXXXXX
XXXXXXXXXXXXXX XXX XXXXXXXXXXXXX
XXXXXXXXXXXXX  XX  XXXXXXXXXXXXX
XXXXXXXXXXXX   X   XXXXXXXXXXXXX
XXXXXXXXXXXXX XXX XXXXXXXXXXXXXX
"""


class PlusIcon(BlackScreen):
    str_grid = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
XXXXXXXXXXXXX       XXXXXXXXXXXX
XXXXXXXXXXXXX       XXXXXXXXXXXX
XXXXXXXXXXXXX       XXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
"""


class HeartIcon(FaceplateGrid):
    str_grid = """
                                
            xx   xx             
           xxxx xxxx            
           xxxxxxxxx            
            xxxxxxx             
             xxxxx              
              xxx               
               x                
"""


class HollowHeartIcon(FaceplateGrid):
    str_grid = """
                                
            xx   xx             
           x  x x  x            
           x   x   x            
            x     x             
             x   x              
              x x               
               x                
"""


class SkullIcon(FaceplateGrid):
    str_grid = """
                                
            xxxxxxx             
           x  xxx  x            
           xxxxxxxxx            
            xxx xxx             
             xxxxx              
             x x x              
             x x x              
"""


class DeadFishIcon(FaceplateGrid):
    str_grid = """
                                
        x          xxxx         
         x  x x x xx xxx        
          xxxxxxxxxxxxxxx       
         x  x x x xxxxxx        
        x          xxxx         
"""


class InfoIcon(BlackScreen):
    str_grid = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXX    XXXXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
XXXXXXXXXXXXXXX    XXXXXXXXXXXXX
"""


class ArrowLeftIcon(BlackScreen):
    str_grid = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXX   XXXXXXXXXXXXXXXX
XXXXXXXXXXXX   XXXXXXXXXXXXXXXXX
XXXXXXXXXXX   X       XXXXXXXXXX
XXXXXXXXXX   X        XXXXXXXXXX
XXXXXXXXXXX   X       XXXXXXXXXX
XXXXXXXXXXXX   XXXXXXXXXXXXXXXXX
XXXXXXXXXXXXX   XXXXXXXXXXXXXXXX
"""


class WarningIcon(BlackScreen):
    str_grid = """
XXXXXXXXXXXXXXX XXXXXXXXXXXXXXXX
XXXXXXXXXXXXXX   XXXXXXXXXXXXXXX
XXXXXXXXXXXXX  X  XXXXXXXXXXXXXX
XXXXXXXXXXXX  XXX  XXXXXXXXXXXXX
XXXXXXXXXXX   XXX   XXXXXXXXXXXX
XXXXXXXXXX           XXXXXXXXXXX
XXXXXXXXX     XXX     XXXXXXXXXX
XXXXXXXX       X       XXXXXXXXX
"""


class CrossIcon(BlackScreen):
    str_grid = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXX XXXXX XXXXXXXXXXXX
XXXXXXXXXXXX   XXX   XXXXXXXXXXX
XXXXXXXXXXXXX   X   XXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
XXXXXXXXXXXXX   X   XXXXXXXXXXXX
XXXXXXXXXXXX   XXX   XXXXXXXXXXX
XXXXXXXXXXXXX XXXXX XXXXXXXXXXXX
"""


class JarbasAI(BlackScreen):
    str_grid = """
X   XXXXXXXXXXXXXXXXXXXXXXX   X 
XX XXXXXXXXXXXXXXXXXXXXXXXX X XX
XX XXXXXXXXXX XXXXXXXXXXXXX X X 
XX XXXXXXXXXX XXXXXXXXX   X   X 
XX XX   X X X    XX   X XXX X X 
 X X XX X  XX XX X XX X   X X X 
 X X XX X XXX XX X XX XXX X X X 
   X    X XXX    X    X   X X X 
"""


class SpaceInvader1(BlackScreen):
    str_grid = """
XXXXXXXXXXXXXX     XXXXXXXXXXXXX
XXXXXXXXXXXXX       XXXXXXXXXXXX
XXXXXXXXXX     x x     XXXXXXXXX
XXXXXXXXXX XX       XX XXXXXXXXX
XXXXXXXXXXXXXX     XXXXXXXXXXXXX
XXXXXXXXXX             XXXXXXXXX
XXXXXXXXXX XXXXXXXXXXX XXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
"""


class SpaceInvader2(BlackScreen):
    str_grid = """
XXXXXXXXXXXXX       XXXXXXXXXXXX
XXXXXXXXXXXX   x x   XXXXXXXXXXX
XXXXXXXXXXXXX       XXXXXXXXXXXX
XXXXXXXXXX X         X XXXXXXXXX
XXXXXXXXXX             XXXXXXXXX
XXXXXXXXXX XXX     XXX XXXXXXXXX
XXXXXXXXXXXXXXX X XXXXXXXXXXXXXX
XXXXXXXXXXXXXXX X XXXXXXXXXXXXXX
"""


class SpaceInvader3(BlackScreen):
    str_grid = """
XXXXXXXXXXXXX       XXXXXXXXXXXX
XXXXXXXXXXXXXXXX XXXXXXXXXXXXXXX
XXXXXXXXXXXXX        XXXXXXXXXXX
XXXXXXXXXXXX   X X   XXXXXXXXXXX
XXXXXXXXXX             XXXXXXXXX
XXXXXXXXXX XX  XXX  XX XXXXXXXXX
XXXXXXXXXXXXXX     XXXXXXXXXXXXX
XXXXXXXXXXXXX  XXX  XXXXXXXXXXXX
"""


class SpaceInvader4(BlackScreen):
    str_grid = """
XXXXXXXXXXXXX       XXXXXXXXXXXX
XXXXXXXXXXXXXXX   XXXXXXXXXXXXXX
XXXXXXXXXXXXX        XXXXXXXXXXX
XXXXXXXXXXXX    X    XXXXXXXXXXX
XXXXXXXXXX             XXXXXXXXX
XXXXXXXXXX XX       XX XXXXXXXXX
XXXXXXXXXXXXXX  X  XXXXXXXXXXXXX
XXXXXXXXXXXXX  XXX  XXXXXXXXXXXX
"""


# Encoded icons
class Boat(BlackScreen):
    encoded = "QIAAABACAGIEMEOEPHAEAGACABABAAAAAA"


# Default weather icons for mark1
class SunnyIcon(FaceplateGrid):
    encoded = "IICEIBMDNLMDIBCEAA"


class PartlyCloudyIcon(FaceplateGrid):
    encoded = "IIEEGBGDHLHDHBGEEA"


class CloudyIcon(FaceplateGrid):
    encoded = "IIIBMDMDODODODMDIB"


class LightRainIcon(FaceplateGrid):
    encoded = "IIMAOJOFPBPJPFOBMA"


class RainIcon(FaceplateGrid):
    encoded = "IIMIOFOBPFPDPJOFMA"


class StormIcon(FaceplateGrid):
    encoded = "IIAAIIMEODLBJAAAAA"


class SnowIcon(FaceplateGrid):
    encoded = "IIJEKCMBPHMBKCJEAA"


class WindIcon(FaceplateGrid):
    encoded = "IIABIBIBIJIJJGJAGA"
