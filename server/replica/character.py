"""
Character component
"""

from pyraknet.bitstream import c_bit, c_uint8, c_uint16, c_uint32, c_uint64, c_int32, c_int64
from pyraknet.replicamanager import Replica

from .component import Component


class Character(Component):
    """
    Character replica
    """
    # TODO: use **kwargs instead of a thousand arguments
    def __init__(self, vehicle=False, vehicle_id=0, level=True, level_num=1, hair_color=0, hair_style=0, shirt_color=0,
                 pants_color=0, eyebrows=0, eyes=0, mouth=0, account_id=1, llog=0, lego_score=0, free_to_play=False,
                 currency_collected=0, bricks_collected=0, smashables_smashed=0, quick_builds=0, enemies_smashed=0,
                 rockets_used=0, missions_completed=0, pets_tamed=0, imagination_powerups=0, life_powerups=0, armor_powerups=0,
                 distance_traveled=0, times_smashed=0, damage_taken=0, damage_healed=0, armor_repaired=0,
                 imagination_restored=0, imagination_used=0, distance_driven=0, airborne_time_race_car=0,
                 racing_imagination_powerups=0, racing_imagination_crates_smashed=0, race_car_boosts=0, race_car_wrecks=0,
                 racing_smashables_smashed=0, races_finished=0, first_place_finishes=0, rocket=False, rocket_characters=0,
                 rocket_modules=[''], glowing_head=False, guild=False, guild_id=0, guild_name='', pvp=False, gm=False, gmlevel=0):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def pre_creation(self, stream):
        """
        Writes part 1 of data
        """
        stream.write(c_bit(True))

        stream.write(c_bit(self.vehicle))

        if self.vehicle:
            stream.write(c_int64(self.vehicle_id))

        stream.write(c_uint8(0))  # NOTE: unknown

        stream.write(c_bit(self.level))

        if self.level:
            stream.write(c_uint32(self.level_num))

        stream.write(c_bit(True))
        stream.write(c_bit(False))
        stream.write(c_bit(True))

    def post_creation(self, stream):
        """
        Writes part 2 of data
        """
        stream.write(c_bit(True))
        stream.write(c_bit(self.pvp))
        stream.write(c_bit(self.gm))
        stream.write(c_uint8(self.gmlevel))
        stream.write(c_bit(False))  # NOTE: unknown
        stream.write(c_uint8(0))  # NOTE: unknown

        stream.write(c_bit(True))
        stream.write(c_uint32(1 if self.glowing_head else 0))

        stream.write(c_bit(self.guild))

        if self.guild:
            stream.write(c_int64(self.guild_id))
            stream.write(self.guild_name, allocated_length=33)
            stream.write(c_bit(True))  # NOTE: unknown
            stream.write(c_int32(-1))  # NOTE: unknown

    def write_construction(self, stream):
        self.pre_creation(stream)

        stream.write(c_bit(False))  # NOTE: unknown flag(?)
        stream.write(c_bit(False))  # NOTE: unknown flag
        stream.write(c_bit(False))  # NOTE: same as above
        stream.write(c_bit(False))  # NOTE: same here

        stream.write(c_uint32(self.hair_color))
        stream.write(c_uint32(self.hair_style))
        stream.write(c_uint32(0))  # NOTE: unknown(?)
        stream.write(c_uint32(self.shirt_color))
        stream.write(c_uint32(self.pants_color))
        stream.write(c_uint32(0))  # NOTE: unknown(?)
        stream.write(c_uint32(0))  # NOTE: unknown(?)
        stream.write(c_uint32(self.eyebrows))
        stream.write(c_uint32(self.eyes))
        stream.write(c_uint32(self.mouth))

        stream.write(c_uint64(self.account_id))
        stream.write(c_uint64(self.llog))
        stream.write(c_uint64(0))  # NOTE: unknown
        stream.write(c_uint64(self.lego_score))

        stream.write(c_bit(self.free_to_play))

        stream.write(c_uint64(self.currency_collected))
        stream.write(c_uint64(self.bricks_collected))
        stream.write(c_uint64(self.smashables_smashed))
        stream.write(c_uint64(self.quick_builds))
        stream.write(c_uint64(self.enemies_smashed))
        stream.write(c_uint64(self.rockets_used))
        stream.write(c_uint64(self.missions_completed))
        stream.write(c_uint64(self.pets_tamed))
        stream.write(c_uint64(self.imagination_powerups))
        stream.write(c_uint64(self.life_powerups))
        stream.write(c_uint64(self.armor_powerups))
        stream.write(c_uint64(self.distance_traveled))
        stream.write(c_uint64(self.times_smashed))
        stream.write(c_uint64(self.damage_taken))
        stream.write(c_uint64(self.damage_healed))
        stream.write(c_uint64(self.armor_repaired))
        stream.write(c_uint64(self.imagination_restored))
        stream.write(c_uint64(self.imagination_used))
        stream.write(c_uint64(self.distance_driven))
        stream.write(c_uint64(self.airborne_time_race_car))
        stream.write(c_uint64(self.racing_imagination_powerups))
        stream.write(c_uint64(self.racing_imagination_crates_smashed))
        stream.write(c_uint64(self.race_car_boosts))
        stream.write(c_uint64(self.race_car_wrecks))
        stream.write(c_uint64(self.racing_smashables_smashed))
        stream.write(c_uint64(self.races_finished))
        stream.write(c_uint64(self.first_place_finishes))

        stream.write(c_bit(False))  # NOTE: unknown(?)

        stream.write(c_bit(self.rocket))

        if self.rocket:
            stream.write(c_uint16(self.rocket_characters))
            # TODO: LDF rocket info

        self.post_creation(stream)

    def serialize(self, stream):
        """
        Serializes the component
        """
        self.pre_creation(stream)
        self.post_creation(stream)
