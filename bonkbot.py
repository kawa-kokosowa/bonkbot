"""BonkBot: Simple IRC bot RPG

Currently bad code revolving around the fact that there's
no easy wa I can find to get all users in a room with pydle.

Lots of stuff doesn't work on connect but works off connect
like self.users actually works

"""

from typing import Union
from functools import partial
import random

import pydle

import messages
from models import (stats_db, countdowns)

#from . import __version__


# You can add as many features as you want! CTCP is worth
# looking at...
CustomBaseClient = pydle.featurize(pydle.features.RFC1459Support)


class BonkBot(pydle.Client):
    """

    Methods which start with `handle_`  are for the various
    keyword actions the user can use anywhere in a message.

    """

    CHANNEL = '#bonk'
    # should be trap pun imo
    NICKNAME = 'BonkBot'

    def on_connect(self) -> None:
        """pydle-override which executes as soon as this
        bot is connected to the server.

        """

        self.join(self.CHANNEL)

    def on_join(self, channel: str, user: str) -> None:
        """nydle-override which runs when a user joins a channel."""

        self.message(user, messages.WELCOME)

    def on_private_message(self, message_author, message):
        """pydle callback called when bot recieves a message in private.

          * STATS:
          * CHAMP
          * LEVELUP
          * NEXT
          * HELP

        """

        private_handlers = [
            'STATS',
            'CHAMP',
            'LEVELUP',
            'NEXT',
            'HELP',
        ]
        self.handler(private_handlers, message, message_author)

    def handler(self, handlers: list, message: str, message_author: str):
        for handler in handlers:
            if handler in message:
                handler_method = getattr(self, 'handle_' + handler.lower())
                handler_method(message, message_author)

    def on_message(self, source: str, message_author: str, message: str):
        try:
            self.part('#general', 'moving to #bonk')
        except:
            pass
        for nickname in self.users:
            if nickname not in stats_db:
                stats_db.new_or_reset(message_author)

    def on_channel_message(self, source: str, message_author: str, message: str) -> None:
        """pydle callback called when a user sends a message in a
        channel this bot has joined.

        "Action keywords" a user can use in a message to run one of its
        associated handlers.:

          * BONK:
          * EVADE:

        """

        self.update_hit_counters(message_author)

        channel_handlers = [
            'BONK',
            'EVADE',
        ]
        self.handler(channel_handlers, message, message_author)
  
    # FIXME bug: what if message is like "I nimbly EVADE person, ..."
    def word_after(self, message: str, word: str, error: dict) -> Union[str, None]:
        try:
            return message.split(word + ' ', 1)[1].split(' ')[0]
        except IndexError:
            error_message = (
                'ERROR:'
                ' You are not using {word} correctly. You must specify'
                ' {specify_what} as the word after {word}.'
                ' Example: "{example}"'
            ).format(message, word=word, **error)
            self.message(error['message_author'], error_message)
            return None

    def handle_bonk(self, message: str, message_author: str) -> None:
        being_hit = self.word_after(
            message,
            'BONK',
            error={
                'specify_what': 'a user (username) to bonk',
                'example': (
                    'I grab my mallet and BONK %s on the head!'
                    % message_author
                ),
                'message_author': message_author,
            },
        )
        if not being_hit:
            return None

        self.message(
            self.CHANNEL,
            "%s has %d messages (not from attacker) "
            "before getting bonked! Speaking EVADE <username> avoids!"
            % (being_hit, stats_db[being_hit]['evasion']),
        )
        already_bonking = [y for x, y in countdowns if x == target]
        if already_bonking:
            self.message(
                self.CHANNEL,
                # FIXME: messages.already_bonking
                "You are already trying to bonk %s!"
                % already_bonking[0]
            )
        else:
            countdowns[(message_author, being_hit)] = stats_db[being_hit]['evasion']

    def handle_evade(self, message: str, message_author: str) -> None:
        evade_who = self.word_after(
            message,
            'EVADE',
            error={
                'specify_what': 'the username of a person bonking you',
                'example': 'I nimbly EVADE %s -- phew!',
                'message_author': message_author,
            },
        )
        if not evade_who:
            return None

        try:
            del countdowns[(evade_who, message_author)]
        except:
            error_message = '%s is not trying to bonk you!' % evade_who
            self.message(message_author, error_message)
            return None

        evade_message = "%s dodged %s!" % (message_author, evade_who)
        self.message(self.CHANNEL, evade_message)

    def handle_next(self, message, message_author: str) -> None:
        """Private message the target the XP needed to level up."""

        self.message(
            message_author,
            messages.X_TO_LEVEL_Y % stats_db.next_level(message_author)
        )

    def handle_levelup(self, message: str, message_author: str) -> None:
        """Handle a requested level up.
        """

        stat = self.word_after(
            message,
            'LEVELUP',
            error={
                'specify_what': 'one of your stats (see: STATS)',
                'example': 'LEVELUP bonking',
                'message_author': message_author,
            },
        )
        if not stat:
            return None

        experience_needed = stats_db.levelup(message_author, stat)
        if experience_needed:
            error_message = (
                "not enough experience (%d to next)!"
                % experience_needed
            )
            self.message(message_author, error_message)
            return None

    def handle_stats(self, message: str, message_author: str) -> None:
        """Send message author a PM with their stats."""
        message = str(stats_db[message_author])
        self.message(message_author, message)

    def handle_champ(self, message: str, message_author: str) -> None:
        message = "The player with the most points is %s (%d)."
        player, points = stats_db.player_hiscore()
        self.message(self.CHANNEL, message % (player, points))

    def handle_help(self, message: str, message_author: str) -> None:
        """Send message author a PM with the help info."""
        self.message(message_author, messages.HELP)

    def knockout(self, murderer, dead_person):
        self.message(
            self.CHANNEL, "%s knocked %s out cold!"
            % (murderer, dead_person)
        )
        points_gained = stats_db.knockout_reward(dead_person)
        self.message(
            self.CHANNEL, "%s gains %d points!"
            % (murderer, points_gained)
        )
        stats_db[murderer]['points'] += points_gained
        stats_db[murderer]['experience'] += points_gained
        stats_db.new_or_reset(dead_person)

    def update_hit_counters(self, message_author: str) -> None:
        # Keep a list of items to remove, because you can't
        # remove items from a dictionary you're iterating over
        delete_these = []

        for attacker, being_hit in countdowns:
            if message_author in (attacker, being_hit):
                continue
            countdowns[(attacker, being_hit)] -= 1
            message_countdown = countdowns[(attacker, being_hit)]

            # If a hit was landed...
            if message_countdown == 0:
                bonking = stats_db.get(attacker, 'bonking')

                if random.randint(1, 10) == 20:
                    self.message(self.CHANNEL, "Critical hit!")
                    bonking *= 2

                stats_db.damage(being_hit, bonking)
                self.message(
                    self.CHANNEL, "%s takes %d damage (attacker: %s)!"
                    % (being_hit, bonking, attacker)
                )

                # If the landed hit killed target
                if stats_db.is_knocked_out(being_hit):
                    self.knockout(attacker, being_hit)

                delete_these.append((attacker, being_hit))

        for key in delete_these:
            del countdowns[key]


pydle.client.PING_TIMEOUT = 172800  # Thinks are slow on this server...
client = BonkBot(BonkBot.NICKNAME, realname='Bonk RPG')
client.connect('irc.y2k.cafe', 6667, tls=False, tls_verify=False, password="idrinkcafe")
client.handle_forever()
