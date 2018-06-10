"""
Player object
"""

from .base_data import BaseData
from .controllable_physics import ControllablePhysics
from .destructible import Destructible
from .stats import Stats
from .character import Character
from .inventory import Inventory
from .script import Script
from .skill import Skill
from .render import Render
from .component107 import Component107

from server.structs import Vector3, Vector4


class Player(BaseData):
    """
    Player replica object
    """
    def __init__(self, char, pos=Vector3(0, 0, 0), rot=Vector4(0, 0, 0, 0)):
        super().__init__(char.pk, 1, char.name)
        control = ControllablePhysics(player=True, player_pos=pos, player_rot=rot)
        destructible = Destructible()
        stats = Stats()
        character = Character(shirt_color=char.shirt_color, hair_style=char.hair_style, hair_color=char.hair_color,
                              pants_color=char.pants_color, eyebrows=char.eyebrows, eyes=char.eyes,
                              account_id=char.account.user.pk)

        inventory = Inventory()
        script = Script()
        skill = Skill()
        render = Render()
        component107 = Component107()

        self.components = [control, destructible, stats, character, inventory, script, skill, render, component107]
