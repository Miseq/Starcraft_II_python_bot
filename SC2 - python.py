import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Player, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, STALKER, ZEALOT
import random
import sc2.constants

class SentendBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.expand()
        await self.build_assimilator()
        await self.build_gateway()
        await self.build_warriors()
        await self.fight()


    async def build_workers(self):
        # nexus - command ceter
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))


    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            where_to_build = self.check_pylons()
            if self.can_afford(PYLON):
                await self.build(PYLON, near=where_to_build, max_distance=50)

    def check_pylons(self):
        if self.units(PYLON).amount > 0:
            return self.units(PYLON)[-1]
        else:
            return self.units(NEXUS).first

    async def expand(self):
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
            await self.expand_now()


    async def build_assimilator(self):
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(25.0, nexus)
            for vasp in vaspenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vasp.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vasp):
                    await self.do(worker.build(ASSIMILATOR, vasp))


    async def build_gateway(self):
        if self.units(PYLON).ready.exists:
            nexus = self.units(NEXUS)[-1]
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=nexus)
            if self.can_afford(GATEWAY) and self.units(GATEWAY).amount < 2:
                await self.build(GATEWAY, near=nexus)

    async def build_warriors(self):
        for gw in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(ZEALOT) and self.units(ZEALOT).amount <= 2.5 * self.units(STALKER).amount:
                await self.do(gw.train(ZEALOT))
            elif self.can_afford(STALKER):
                await self.do(gw.train(STALKER))

    async def fight(self):
        if self.units(STALKER).amount > 3:
            units = self.units(STALKER).idle + self.units(ZEALOT).idle
            for unit in units:
                await self.do(unit.attack(self.find_enemy(self.state)))

        elif self.units(ZEALOT).amount > 0 and len(self.known_enemy_units) > 0:
            for unit in self.units(ZEALOT).idle:
                await self.do(unit.attack(self.known_enemy_units[-1]))

    def find_enemy(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]


run_game(maps.get("AbyssalReefLE"),
        [Bot(Race.Protoss,SentendBot()), Computer(Race.Terran, Difficulty.Easy)], realtime=False)