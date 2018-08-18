import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Player, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE,\
    STALKER, ZEALOT, VOIDRAY, STARGATE
import random
import sc2.constants

class SentendBot(sc2.BotAI):

    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 65

    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.expand()
        await self.build_assimilator()
        await self.build_offensive_buildings()
        await self.build_warriors()
        await self.fight()


    async def build_workers(self):
        # nexus - command ceter
        if len(self.units(NEXUS)) * 16 > len(self.units(PROBE)):
            if len(self.units(PROBE)) < self.MAX_WORKERS:
                for nexus in self.units(NEXUS).ready.noqueue:
                    if self.can_afford(PROBE):
                        await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near= nexuses.first)


    async def expand(self):
        if self.units(NEXUS).amount < (self.iteration / self.ITERATIONS_PER_MINUTE) / 2 and self.can_afford(NEXUS):
            await self.expand_now()
            #IT's perfect <crying>


    async def build_assimilator(self):
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vasp in vaspenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vasp.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vasp):
                    await self.do(worker.build(ASSIMILATOR, vasp))


    async def build_offensive_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).random

            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTE) / 4 ):
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                        await self.build(STARGATE, near=pylon)

            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)

            elif self.can_afford(GATEWAY) and self.units(GATEWAY).amount < ((self.iteration / self.ITERATIONS_PER_MINUTE) / 4):
                await self.build(GATEWAY, near=pylon)



    async def build_warriors(self):
        for gw in self.units(GATEWAY).ready.noqueue:
            if not self.units(STALKER).amount > self.units(VOIDRAY).amount:
                if self.can_afford(STALKER) and self.supply_left > 0:
                    await self.do(gw.train(STALKER))

        for sg in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY):
                    await self.do(sg.train(VOIDRAY))
            #TODO there has to be a simpler way

    async def fight(self):
        army = {STALKER: [10, 3], VOIDRAY: [8,3]}

        for unit in army:
            if self.units(unit).amount > army[unit][0]:
                for meat in self.units(unit).idle:
                    await self.do(meat.attack(self.find_enemy(self.state)))

            elif self.units(unit).amount > army[unit][1] and len(self.known_enemy_units) > 0:
                for meat in self.units(unit).idle:
                    await self.do(meat.attack(random.choice(self.known_enemy_units)))
        #TODO it sucks

    def find_enemy(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]


run_game(maps.get("AbyssalReefLE"),
        [Bot(Race.Protoss,SentendBot()), Computer(Race.Terran, Difficulty.Hard)], realtime=False)