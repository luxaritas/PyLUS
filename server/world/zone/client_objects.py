"""
Provides client objects from LUZ/LVL files and CDClient
Portions of LUZReader influenced by LCDR's utils/luzviewer https://bitbucket.org/lcdr/utils/src/default/luzviewer.pyw
"""

import os
import logging
log = logging.getLogger(__name__)
import random
import sqlite3

from pyraknet.bitstream import ReadStream, WriteStream, c_uint8, c_uint16, c_uint64, \
                               c_int, c_int64, c_bit, c_ubyte, c_uint, c_int, c_ushort, c_float

from server.plugin import Plugin, Action
from server.structs import Vector3, Vector4, LVLVector4, parse_ldf
from server.enums import ZONE_IDS, ZONE_LUZ

from server.replica import BaseData
from server.replica import SimplePhysics
from server.replica import Render
from server.replica import Script
from server.replica import ControllablePhysics
from server.replica import Character
from server.replica import Destructible
from server.replica import Skill
from server.replica import Component107
from server.replica import PhantomPhysics
from server.replica import Bouncer
from server.replica import Rebuild
from server.replica import Stats

class ClientObjectLoader(Plugin):
    """
    Provides data from LUZ/LVL files
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.luz = LUZReader(ZONE_LUZ[ZONE_IDS[self.server.type]], self.server.type)
        for scene in self.luz.scenes:
            for obj in scene.objects:
                if obj.spawner is not None:
                    trigger = obj.config.get('renderDisabled')
                    components = obj.components

                    if trigger:
                        trigger_comp = Trigger()

                        components.append(trigger_comp)

                    replica = BaseData(obj.objid, obj.lot, obj.name, trigger=trigger, spawner=obj.spawner, scale=obj.scale, components=components)

                    wstr = WriteStream()
                    wstr.write(c_uint8(0x24))
                    wstr.write(c_bit(True))
                    wstr.write(c_uint16(0))
                    replica.write_construction(wstr)

                    self.server.repman.construct(replica, True)

    def actions(self):
        return []

class LUObject:
    """
    LEGO Universe world object
    """
    def __init__(self, objid, lot, pos, rot, scale, config, spawner, conn):
        self.objid = objid
        self.lot = lot
        self.position = pos
        self.rotation = rot
        self.scale = scale
        self.config = config
        self.spawner = spawner
        self.conn = conn
        self.components = self.get_components()
        print(f'****** {self.name} x {self.position.x} y {self.position.y} z {self.position.z}')

    @property
    def name(self):
        """
        Returns the name for this object
        """
        return self.conn.execute('SELECT name FROM Objects WHERE id = ?', (self.lot,)).fetchone()[0]

    def get_components(self):
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
                    Stats(stats=False),
                    Rebuild(activator_pos=Vector3.from_ldf(self.config['rebuild_activators'])),
                ]
            elif comp_type == 107:
                component = Component107()
            else:
                log.debug(f'Unhandled component type in {self.name}: {comp_type}')

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
    def __init__(self, file, server_zone):
        self.conn = sqlite3.connect('client_assets/cdclient.sqlite')
        self.scenes = []

        with open(file, 'rb') as file:
            self.data = file.read()
            self.size = len(self.data)
            self.stream = ReadStream(self.data, unlocked=True)

        self.version = self.stream.read(c_uint)
        assert self.version in (36, 38, 39, 40, 41), 'Unknown LUZ version ' + self.version
        self.unknown1 = self.stream.read(c_uint)
        self.world_id = self.stream.read(c_uint)

        if self.version >= 38:
            self.spawnpoint = Vector3(self.stream.read(c_float), self.stream.read(c_float), self.stream.read(c_float))
            self.spawnpoint_rot = LVLVector4(self.stream.read(c_float), self.stream.read(c_float), self.stream.read(c_float),
                                          self.stream.read(c_float))
        else:
            # TODO: Verify what should actually happen in versions < 38
            self.spawnpoint = Vector3(0,0,0)
            self.spawnpoint_rot = Vector4(0,0,0,0)

        if self.version >= 37:
            self.num_scenes = self.stream.read(c_uint)
        else:
            self.num_scenes = self.stream.read(c_ubyte)

        for _ in range(self.num_scenes):
            filename = self.stream.read(bytes, length_type=c_ubyte).decode('latin1')
            scene_id = self.stream.read(c_uint64)
            scene_name = self.stream.read(bytes, length_type=c_ubyte).decode('latin1')
            assert self.stream.read(bytes, length=3)
            lvl_path = os.path.join('client_assets', 'lvl', server_zone, filename)

            if os.path.exists(lvl_path):
                with open(lvl_path, 'rb') as file:
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
                assert stream.read_offset // 8 % 16 == 0, 'Invalid LVL chunk read offset'
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

            position = stream.read(Vector3)
            rotation = stream.read(LVLVector4)
            scale = stream.read(c_float)

            config_data = parse_ldf(stream.read(str, length_type=c_uint))

            assert stream.read(c_uint) == 0

            if config_data.get('renderDisabled'):
                continue

            spawner=None
            if lot == 176:
                spawner=objid
                lot = config_data['spawntemplate']
                objid = random.randint(1000000000000000000, 1999999999999999999)

            obj = LUObject(objid, lot, position, rotation, scale, config_data, spawner, self.conn)
            objects.append(obj)

        return objects
