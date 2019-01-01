"""
Character
"""

from datetime import timedelta

import random

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from cms.game.models import Character, Account, Mission

from server.plugin import Plugin, Action


class DjangoCharacterPersistence(Plugin):
    """
    Character persistence plugin
    """
    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('char:characters', self.get_characters, 10),
            Action('char:front_char', self.get_front_character, 10),
            Action('char:create_character', self.create_character, 10),
            Action('char:get_character', self.get_character, 10),
            Action('char:get_missions', self.get_missions, 10),
            Action('char:complete_mission', self.complete_mission, 10),
            Action('char:activate_mission', self.activate_mission, 10),
            Action('char:initial_zone', self.get_last_zone, 10),
            Action('world:zone_entered', self.set_last_zone, 10),
        ]

    def create_character(self, account, name, unapproved_name, name_rejected, shirt_color, shirt_style, pants_color,
                         hair_style, hair_color, lh, rh, eyebrows, eyes, mouth, last_zone, last_instance, last_clone):
        """
        Creates a character
        """
        # TODO: Actually set the OBJID correctly
        return Character.objects.create(objid=random.randint(1000000000000000000, 1999999999999999999),
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
                                 last_login=0)

    def get_characters(self, account):
        """
        Returns all characters for a user
        """
        return account.character_set.all()

    def get_character(self, char_id):
        """
        Returns the character with that id
        """
        return Character.objects.get(pk=char_id)

    def get_front_character(self, characters):
        """
        Get the front character for a user
        """
        filtered = list(filter(lambda char: char.is_front, characters))
        if len(filtered) == 0:
            return None
        return filtered[0]

    def get_missions(self, char_id):
        """
        Returns missions for a character
        """
        return Mission.objects.filter(character__pk=char_id)

    def complete_mission(self, char_id, mission_id):
        """
        Completes a mission
        """
        mission = Mission.objects.get(mission=mission_id, character__pk=char_id)
        mission.state = 8
        mission.times_completed += 1
        mission.save()

    def activate_mission(self, char_id, mission_id):
        """
        Activates a mission
        """
        Mission(mission=mission_id, character__pk=char_id, state=2, times_completed=0, last_completion=0).save()

    def get_last_zone(self, char):
        """
        Gets zone to redirect to on client request
        """
        return char.last_zone

    def set_last_zone(self, session, zone_id):
        session.character.last_zone = zone_id
        session.character.save()
