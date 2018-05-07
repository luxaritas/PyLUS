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
            Action('char:create_character', self.create_character, 10),
            Action('char:get_character', self.get_character, 10),
        ]

    def create_character(self, uid, slot, name, unapproved_name, name_rejected, shirt_color, shirt_style, pants_color,
                         hair_style, hair_color, lh, rh, eyebrows, eyes, mouth, last_zone, last_instance, last_clone,
                         last_login):
        """
        Creates a character
        """
        account = Account.objects.get(user__pk=uid)

        Character.objects.create(slot=slot,
                                 account=account,
                                 name=name,
                                 unapproved_name=unapproved_name,
                                 is_name_rejected=name_rejected,
                                 shirt_color=shirt_color,
                                 shirt_style=shirt_style,
                                 pants_color=pants_color,
                                 hair_style=hair_style,
                                 hair_color=hair_color,
                                 lh=lh,
                                 rh=rh,
                                 eyebrows=eyebrows,
                                 eyes=eyes,
                                 mouth=mouth,
                                 last_zone=last_zone,
                                 last_instance=last_instance,
                                 last_clone=last_clone,
                                 last_login=last_login)

    def get_characters(self, uid):
        """
        Returns all characters for a user
        """
        return Character.objects.all().filter(account__user__pk=uid)

    def get_character(self, char_id):
        """
        Returns the character with that id
        """
        return Character.objects.get(id=char_id)

    def get_front_character(self, uid):
        """
        Get the front character for a user
        """
        account = Account.objects.get(user__pk=uid)
        return account.front_character
