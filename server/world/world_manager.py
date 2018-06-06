"""
World manager
"""

import random
import sqlite3

from server.enums import ZONE_LUZ
from server.plugin import Plugin, Action
from server.luzreader import LUZReader


class WorldManager(Plugin):
    """
    World manager class
    """
    conn = sqlite3.connect('client_assets/cdclient.sqlite')
    cache = {}
    clones = []

    def actions(self):
        """
        Returns the actions
        """
        return [
            Action('world:get_zone_luz', self.get_zone_luz, 10),
            Action('world:join', self.join_world, 10),
            Action('world:get_clone', self.get_clone, 10),
            Action('world:get_clone_id', self.get_clone_id, 10),
            Action('world:missions_for_lot', self.missions_for_lot, 10),
            Action('world:missions_for_lot_target', self.missions_for_lot_target, 10),
            Action('world:get_mission', self.get_mission, 10),
            Action('world:get_mission_tasks', self.get_mission_tasks, 10),
            Action('world:mission_prereq', self.mission_prereq, 10),
        ]

    def packets(self):
        """
        Returns the packets
        """
        return []

    def get_zone_luz(self, zone):
        luz = self.cache[zone] if zone in self.cache else LUZReader(ZONE_LUZ[zone], self.conn)

        if zone not in self.cache:
            self.cache[zone] = luz

        return luz

    def join_world(self, uid, objid, zone):
        """
        Have a user join a world
        """
        if len([clone for clone in self.clones if clone.zone == zone]) == 0:
            luz = self.get_zone_luz(zone)

            clone = WorldClone(zone, luz)
            self.clones.append(clone)
            clone.join(uid, objid, zone)

            return clone

        for clone in self.clones:
            if clone.join(uid, objid, zone):
                return clone

    def get_clone(self, clone):
        """
        Returns a world clone
        """
        return self.clones[clone]

    def get_clone_id(self, clone):
        """
        Returns a clone id
        """
        return self.clones.index(clone)

    def missions_for_lot(self, lot):
        """
        Returns missions offered by the LOT
        """
        return self.conn.execute('SELECT * FROM Missions WHERE offer_objectID = ?', (lot,)).fetchall()

    def missions_for_lot_target(self, lot):
        """
        Returns missions with LOT as target
        """
        return self.conn.execute('SELECT * FROM Missions WHERE target_objectID = ?', (lot,)).fetchall()

    def get_mission(self, mission):
        """
        Returns a mission from the cdclient
        """
        return self.conn.execute('SELECT * FROM Missions WHERE id = ?', (mission,)).fetchone()

    def get_mission_tasks(self, mission):
        """
        Returns tasks for a mission from the cdclient
        """
        return self.conn.execute('SELECT * FROM MissionTasks WHERE id = ?', (mission,)).fetchall()

    def mission_prereq(self, mission):
        """
        Returns missions that have the mission as prerequirement
        """
        return self.conn.execute('SELECT * FROM Missions WHERE prereqMissionID = ?', (mission,)).fetchall()


class WorldClone:
    def __init__(self, zone, luz, instance=0, max_players=32):
        self.zone = zone
        self.instance = instance
        self.max_players = max_players
        self.spawn = luz.spawnpoint
        self.spawn_rotation = luz.spawnpoint_rot
        self.players = []
        self.objects = []

        for scene in luz.scenes:
            for obj in scene.objects:
                obj.objid = random.randint(100000000000000000, 999999999999999999)
                self.objects.append(obj)

    def join(self, uid, objid, zone):
        if zone != self.zone:
            return False

        if len(self.players) < self.max_players:
            self.players.append({'uid': uid, 'objid': objid})
            return True
        else:
            return False
