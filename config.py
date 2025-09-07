#========================#
#    Default Config      #
#========================#

#----Map Init----#
GRID_SIZE = 250                    # Size of the map (GRID_SIZE x GRID_SIZE)
NUM_CIVS = 20                      # Number of civilizations
SEED = None                        # Set to None to randomize
    
#----Map Config----#       
SCALE = 75.0                       # Zoom - 100 (closer) 1 (farther)
OCTAVES = 6                        # Complexity - 1 (simple) 10 (complex)
PERSISTENCE = 0.5                  # Roughness - 0 (smooth) 1 (rough)
LACUNARITY = 2.0                   # Detail/Texture - 1 (smooth) 10 (detailed)
LAND_THRESHOLD = 0.4               # Water Level - 0 (all land) 1 (all water)
    
#----Civ Logic Config----#   
# Expansion  
BASE_EXPANSION_CHANCE = 0.5        # Base chance of expansion
EXPANSION_SCALE_FACTOR = 500       # How much civ size affects expansion chance
GROUP_PUSH_LIMIT = 60              # Max number of expansions per civ per frame
WAR_INTENSITY_GROWTH = 0.1         # How much war intensity grows per frame
MULTI_FRONT_SCALING = 0.2          # How much multi-front wars increase expansion chance
# Speed
SPEED_MULTIPLIER = 1               # How many frames to process per update
# Cooldowns
WAR_COOLDOWN = 50                  # Frames before a civ can declare war again
PEACE_TREATY_COOLDOWN = 100        # Frames before a peace treaty expires
# Chances
PEACE_CHANCE = 0.005               # Chance of peace treaty per frame
# Limits
MAX_WARS = 5                       # Max number of wars allowed at once
ANNEXATION_THRESHOLD = 0.3         # How much of a civ's territory must be disconnected to anne