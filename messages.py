# FIXME: hack for now
__version__ = '0.0.0'

HELP = """
Bonk RPG IRC Bot v%s
Silvia SoftWorks

Bonk players until they are knocked out and take their points!

Bonking a player starts a countdown starting at the target's
EVASION stat. Each message sent (not from attacker) decrements
this counter.

ACTION KEYWORDS:
    Use case-sensitive ACTION KEYWORDS anywhere in a message in order
    to perform that action. For example, "I grab my mallet and BONK
    Alice on the head!"

CHANNEL ACTION KEYWORDS:
    Use these ACTION KEYWORDS in a channel.

    BONK <username>: use `BONK <username>` anywhere in a CHANNEL
        message, but replace `<username>` with the actual username!
    EVADE <username>: dodge a user's BONK, must occur before countdown
        reaches 0.

PRIVATE ACTION KEYWORDS:
    Private message these ACTION KEYWORDS to me (the bot!).

    HELP: display this message.
    NEXT: get a private message with the amount of XP to next level.
    CHAMP: publicly display the player with most points.
    STATS: get a private message about your player stats.

STATS:
    BONKING: Damage dealt if BONK is not evaded. When BONK does land,
        there's a chance it'll be a "critical hit," doubling damage.
    EVASION: # of messages before you're BONK'd; if you send a message
        with "EVADE" in it before then you dodge the BONK!
    MAX_HEALTH: Your total health.
    CURRENT_HEALTH: You lose everything when this reaches 0.
    EXPERIENCE: you can spend this on leveling up.
    POINTS: score; the point of the game, get the highest!
    LEVEL: how many times you've leveled up.
""" % __version__

WELCOME = "Welcome new user!"

X_TO_LEVEL_Y = "%d to level %d"
