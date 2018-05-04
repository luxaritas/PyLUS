"""
Character
"""

from datetime import datetime, timedelta

import bcrypt

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from cms.game.models import Character, Account

from plugin import Plugin, Action


class DjangoCharacterList(Plugin):
    """
    Character list plugin
    """
    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('char:characters', self.get_characters, 10),
            Action('char:front_char_index', self.get_front_character, 10),
        ]

    def get_characters(self, uid):
        """
        Returns all characters for a user
        """
        characters = Character.objects.get(account__user__pk=uid)
        return characters

    def get_front_character(self, uid):
        """
        Get the front character for a user
        """
        account = Account.objects.get(user__pk=uid)
        return account.front_character
