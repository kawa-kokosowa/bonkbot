from typing import Union

STARTING_STATS = {
    'bonking': 1,
    'evasion': 3,
    'current_health': 5,
    'max_health': 5,
    'points': 2,
    'level': 1,
    'experience': 2,
}
"""dict: stats you start with and level up by"""


class Stats:

    def __init__(self):
        self._records = {}

    def hiscore(self) -> tuple:
        player_hiscore = (None, 0)
        for player in self._records:
            points = self._records[player]['points']
            if points > player_hiscore[1]:
                player_hiscore = (player, points)
        return player_hiscore

    def damage(self, username: str, damage: int) -> None:
        self._records[username]['current_health'] -= damage

    def levelup(self, message_author: str, stat: str) -> Union[tuple, None]:
        if not self.can_level_up(message_author):
            return self.next_level(message_author)[0]

        if stat == 'HEALTH':
            stats_db[message_author]['max_health'] += STARTING_STATS['max_health']
            stats_db[message_author]['current_health'] = stats_db['message_author']['max_health']
        else:
            stats_db[message_author][stat] += STARTING_STATS[stat]

        stats_db[message_author]['experience'] -= self.next_level(message_author)[0]
        stats_db[message_author]['level'] += 1

    def is_knocked_out(self, username: str) -> bool:
        return self._records[username]['current_health'] < 1

    def next_level(self, username: str) -> tuple:
        experience = self._records[username]['experience']
        level = self._records[username]['level']
        xp_to_next_level = (self._records[username]['level'] * 5) - experience
        return (xp_to_next_level, level + 1)

    def can_level_up(self, username: str):
        return stats_db[username]['experience'] >= self._records[username]['level'] * 5

    def get(self, username: str, stat: str):
        return self._records[username][stat]

    def new_or_reset(self, username):
        self._records[username] = STARTING_STATS.copy()

    def knockout_reward(self, username: str):
        return self._records[username]['points'] // 2

    def __contains__(self, key):
        return key in self._records

    def __getitem__(self, key):
        return self._records[key]

    def __setitem__(self, key, value):
        self._records[key] = value

    def __delitem__(self, key):
        del self._records[key]


stats_db = Stats()

# FIXME: better docstring
countdowns = {}
"""dict: Database/record of how many messages until a bonk lands."""
