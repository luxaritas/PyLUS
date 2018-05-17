"""
Player object
"""

from replica.base_data import BaseData
from replica.controllable_physics import ControllablePhysics
from replica.destructible import Destructible
from replica.stats import Stats
from replica.character import Character
from replica.inventory import Inventory
from replica.script import Script
from replica.skill import Skill
from replica.render import Render
from replica.component107 import Component107

from structs import Vector3, Vector4


class Player(BaseData):
    """
    Player replica object
    """
    def __init__(self, char, pos=Vector3(0, 0, 0), rot=Vector4(0, 0, 0, 0)):
        super().__init__(char.id, 1, char.name)
        control = ControllablePhysics(player=True, player_pos=pos, player_rot=rot)
        destructible = Destructible()
        stats = Stats()
        character = Character(shirt_color=char.shirt_color, hair_style=char.hair_style, hair_color=char.hair_color,
                              pants_color=char.pants_color, eyebrows=char.eyebrows, eyes=char.eyes,
                              account_id=char.account.user.id)

        inventory = Inventory()
        script = Script()
        skill = Skill()
        render = Render()
        component107 = Component107()

        self.components = [control, destructible, stats, character, inventory, script, skill, render, component107]
