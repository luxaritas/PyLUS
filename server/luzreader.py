"""
.luz file reader
"""

import sqlite3
import os.path

from pyraknet.bitstream import ReadStream, c_uint, c_float, c_ubyte, c_uint64, c_ushort, c_int64

from .replica.simple_physics import SimplePhysics
from .replica.render import Render
from .replica.script import Script
from .replica.controllable_physics import ControllablePhysics
from .replica.character import Character
from .replica.destructible import Destructible
from .replica.skill import Skill
from .replica.component107 import Component107
from .replica.phantom_physics import PhantomPhysics
from .replica.bouncer import Bouncer
from .replica.rebuild import Rebuild
from .replica.stats import Stats

from .structs import Vector3, Vector4, parse_ldf


class LUObject:
    """
    LEGO Universe world object
    """
    def __init__(self, objid, lot, pos, rot, scale, config, conn=None):
        self.objid = objid
        self.lot = lot
        self.position = pos
        self.rotation = rot
        self.scale = scale
        self.config = config
        self.conn = conn

    @property
    def name(self):
        """
        Returns the name for this object
        """
        return self.conn.execute('SELECT name FROM Objects WHERE id = ?', (self.lot,)).fetchone()[0]

    @property
    def components(self):
        """
        Returns all components for this object
        """
        order = [108, 61, 1, 3, 20, 30, 40, 7, 23, 26, 4, 19, 17, 5, 9, 60, 48, 25, 49, 16, 6, 39, 71, 75, 42, 2, 50, 107, 69, 116]

        sorted_order = sorted(order)
        nums = [x for x in range(sorted_order[0], sorted_order[-1] + 1)]
        order += list(set(order) ^ set(nums))

        order_dict = {k: v for v, k in enumerate(order)}

        comps = self.conn.execute('SELECT * FROM ComponentsRegistry WHERE id = ?', (self.lot,)).fetchall()

        comps.sort(key=lambda x: order_dict.get(x[1]))

        components = []

        for comp in comps:
            comp_type = comp[1]

            component = None

            if comp_type == 1:
                component = ControllablePhysics(player_pos=self.position, player_rot=self.rotation)
            elif comp_type == 2:
                component = Render(self.config.get('renderDisabled', False))
            elif comp_type == 3:
                component = SimplePhysics(self.position, self.rotation)
            elif comp_type == 4:
                component = Character()  # TODO: read stuff from config?
            elif comp_type == 5:
                component = Script()  # TODO: read stuff from config?
            elif comp_type == 6:
                component = Bouncer()
            elif comp_type == 7:
                component = Destructible()
            elif comp_type == 9:
                component = Skill()  # TODO: read stuff from config?
            elif comp_type == 40:
                component = PhantomPhysics(self.position, self.rotation)  # TODO: read stuff from config?
            elif comp_type == 48:
                component = [
                    Script(script=False),
                    Stats(stats=False),
                    Rebuild(activator_pos=Vector3.from_ldf(self.config['rebuild_activators'])),
                ]
            elif comp_type == 107:
                component = Component107()
            else:
                print(f'Unhandled component type in {self.name}: {comp_type}')

            if component:
                if isinstance(component, list):
                    components.extend(component)
                else:
                    components.append(component)

        return components


class LUScene:
    """
    LEGO Universe scene
    """
    def __init__(self, id, name, objects=[]):
        self.id = id
        self.name = name
        self.objects = objects


class LUZReader:
    """
    LEGO Universe Zone file reader
    """
    def __init__(self, file, conn=None):
        self.conn = conn or sqlite3.connect('cdclient.sqlite')
        self.scenes = []

        with open(file, 'rb') as file:
            self.data = file.read()
            self.size = len(self.data)
            self.stream = ReadStream(self.data, unlocked=True)

        self.version = self.stream.read(c_uint)
        assert self.version == 41, self.version
        self.unknown1 = self.stream.read(c_uint)
        self.world_id = self.stream.read(c_uint)

        self.spawnpoint = Vector3(self.stream.read(c_float), self.stream.read(c_float), self.stream.read(c_float))
        self.spawnpoint_rot = Vector4(self.stream.read(c_float), self.stream.read(c_float), self.stream.read(c_float),
                                      self.stream.read(c_float))

        self.num_scenes = self.stream.read(c_uint)

        for _ in range(self.num_scenes):
            filename = self.stream.read(bytes, length_type=c_ubyte).decode('latin1')
            scene_id = self.stream.read(c_uint64)
            scene_name = self.stream.read(bytes, length_type=c_ubyte).decode('latin1')
            assert self.stream.read(bytes, length=3)
            pth = os.path.join('luz', filename)

            if os.path.exists(pth):
                with open(pth, 'rb') as file:
                    objects = self.get_lvl_objects(ReadStream(file.read(), unlocked=True))
                    self.scenes.append(LUScene(scene_id, scene_name, objects))
            else:
                self.scenes.append(LUScene(scene_id, scene_name))

    def get_lvl_objects(self, stream):
        """
        Parses a level file and returns its objects
        """
        header = stream.read(bytes, length=4)
        objects = []

        stream.read_offset = 0

        if header == b'CHNK':
            while not stream.all_read():
                assert stream.read_offset // 8 % 16 == 0
                start_pos = stream.read_offset // 8
                assert stream.read(bytes, length=4) == b'CHNK'

                chunk_type = stream.read(c_uint)
                assert stream.read(c_ushort) == 1
                assert stream.read(c_ushort) in (1, 2)
                chunk_len = stream.read(c_uint)
                data_pos = stream.read(c_uint)
                stream.read_offset = data_pos * 8
                assert stream.read_offset // 8 % 16 == 0

                if chunk_type == 1000:
                    pass
                elif chunk_type == 2000:
                    pass
                elif chunk_type == 2001:
                    objects = self.parse_chunk_2001(stream)
                elif chunk_type == 2002:
                    pass

                stream.read_offset = (start_pos + chunk_len) * 8

        return objects

    def parse_chunk_2001(self, stream):
        """
        Parses chunk 2001
        """
        objects = []

        for _ in range(stream.read(c_uint)):
            objid = stream.read(c_int64)
            lot = stream.read(c_uint)
            unknown1 = stream.read(c_uint)
            unknown2 = stream.read(c_uint)
            position = Vector3(stream.read(c_float), stream.read(c_float), stream.read(c_float))

            rot_w = stream.read(c_float)
            rot_z = stream.read(c_float)
            rot_y = stream.read(c_float)
            rot_x = stream.read(c_float)

            rotation = Vector4(rot_x, rot_y, rot_z, rot_w)
            scale = stream.read(c_float)
            config_data = parse_ldf(stream.read(str, length_type=c_uint))

            assert stream.read(c_uint) == 0

            if config_data.get('renderDisabled'):
                continue

            if lot == 176:
                lot = config_data['spawntemplate']

            # if lot == 4638:
            #     continue

            obj = LUObject(objid, lot, position, rotation, scale, config_data, self.conn)
            objects.append(obj)

        return objects
