debug = False

# Definitions of Zandronum constant values
# These are unlikely to change, except possibly in a major new Zandronum release or re-write

# Server flags:
# These are hexadecimal 32-bit unsigned values ("long integers")
# They are pulled directly from: https://wiki.zandronum.com/Launcher_protocol

# We will use a bitwise OR operator on the flags we want, and the resulting value will be what we send
# to the server as our request
SQF_NAME = int("0x00000001", 16)  # The name of the server
SQF_URL = int("0x00000002", 16)  # The associated website
SQF_EMAIL = int("0x00000004", 16)  # Contact address
SQF_MAPNAME = int("0x00000008", 16)  # Current map being played
SQF_MAXCLIENTS = int("0x00000010", 16)  # Maximum amount of clients who can connect to the server
SQF_MAXPLAYERS = int("0x00000020", 16)  # Maximum amount of players who can join the game (the rest must spectate)
SQF_PWADS = int("0x00000040", 16)  # PWADs loaded by the server
SQF_GAMETYPE = int("0x00000080", 16)  # Game type code
SQF_GAMENAME = int("0x00000100", 16)  # Game mode name
SQF_IWAD = int("0x00000200", 16)  # The IWAD used by the server
SQF_FORCEPASSWORD = int("0x00000400", 16)  # Whether or not the server enforces a password
SQF_FORCEJOINPASSWORD = int("0x00000800", 16)  # Whether or not the server enforces a join password
SQF_GAMESKILL = int("0x00001000", 16)  # The skill level on the server
SQF_BOTSKILL = int("0x00002000", 16)  # The skill level of any bots on the server
SQF_DMFLAGS = int("0x00004000",
                  16)  # (Deprecated) The values of dmflags, dmflags2 and compatflags. Use SQF_ALL_DMFLAGS instead.
SQF_LIMITS = int("0x00010000", 16)  # Timelimit, fraglimit, etc.
SQF_TEAMDAMAGE = int("0x00020000", 16)  # Team damage factor.
SQF_TEAMSCORES = int("0x00040000", 16)  # (Deprecated) The scores of the red and blue teams. Use SQF_TEAMINFO_* instead.
SQF_NUMPLAYERS = int("0x00080000", 16)  # Amount of players currently on the server.
SQF_PLAYERDATA = int("0x00100000", 16)  # Information of each player in the server.
SQF_TEAMINFO_NUMBER = int("0x00200000", 16)  # Amount of teams available.
SQF_TEAMINFO_NAME = int("0x00400000", 16)  # Names of teams.
SQF_TEAMINFO_COLOR = int("0x00800000", 16)  # RGB colors of teams.
SQF_TEAMINFO_SCORE = int("0x01000000", 16)  # Scores of teams.
SQF_TESTING_SERVER = int("0x02000000",
                         16)  # Whether or not the server is a testing server, also the name of the testing binary.
SQF_DATA_MD5SUM = int("0x04000000",
                      16)  # (Deprecated) Used to retrieve the MD5 checksum of skulltag_data.pk3, now obsolete and returns an empty string instead.
SQF_ALL_DMFLAGS = int("0x08000000", 16)  # Values of various dmflags used by the server.
SQF_SECURITY_SETTINGS = int("0x10000000",
                            16)  # Security setting values (for now only whether the server enforces the master banlist)
SQF_OPTIONAL_WADS = int("0x20000000", 16)  # Which PWADs are optional
SQF_DEH = int("0x40000000", 16)  # List of DEHACKED patches loaded by the server.

# Default data to request when querying a server
# This is a bitwise OR of all the flags we want to get info about
#
# This is important, as it will determine how we parse the answer!
DEFAULT_FLAGS = int(
    SQF_NAME |
    SQF_URL |
    SQF_EMAIL |
    SQF_MAPNAME |
    SQF_MAXPLAYERS |
    SQF_PWADS |
    SQF_GAMETYPE |
    SQF_GAMENAME |
    SQF_IWAD |
    SQF_GAMESKILL |
    SQF_LIMITS |
    SQF_NUMPLAYERS |
    SQF_PLAYERDATA).to_bytes(4, "little")

# Game mode labels - order matters here!
# There are 16 modes, numbered 0 - 15 in this order:
GAMEMODE = ["Cooperative", "Survival", "Invasion", "Deathmatch", "Team Deathmatch", "Duel", "Terminator",
            "Last Man Standing", "Team Last Man Standing", "Possession", "Team Possession", "Team Game",
            "Capture the Flag", "One-Flag Capture the Flag", "Skull Tag", "Domination"]

# Skill labels:
# Doom skill modes, 1-5.  Order matters in this list
SKILL = ["I'm too young to die", "Hey, not too rough", "Hurt me plenty", "Ultra-violence", "Nightmare!"]

# Template labels:
# These are a list of template "codes" (macros) that can be replaced with actual server values 
# in an output

Templates = ["%ZVersion%",
             "%serverName%",
             "%serverURL%",
             "%serverEmail%",
             "%serverMap%",
             "%maxPlayers%",
             "%serverGame%",
             "%serverIwad%",
             "%serverSkill%",
             "%pwadCount%",
             "%pwadList%",
             "%serverType%",
             "%instaGib%",
             "%buckShot%",
             "%teamGame%",
             "%fragLimit%",
             "%timeLimit%",
             "%timeLeft%",
             "%duelLimit%",
             "%pointLimit%",
             "%winLimit%",
             "%clientCount%",
             "%currentTime%",
             "%serverIP%",
             "%serverPort%"
             ]

# These templates all involve player-specific macros
PlayerTemplates = ["%playerName%",
                   "%playerPing%",
                   "%playerScore%",
                   "%playerSpectate%",
                   "%playerIsBot%",
                   "%playerTeamNumber%",
                   "%playerMinutes%"
                   ]
