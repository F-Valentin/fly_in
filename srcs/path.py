from zone import Zone
from zone import ZoneState
from drone import Drone


class Path:
    def __init__(self, path: list[Zone], cost: int = 0,
                 nb_of_priority_zones: int = 0) -> None:
        self.path = path
        self.cost = cost
        self.total_cast = 0
        self.nb_of_priority_zones = 0
        self.drones: list[Drone] = []

        self.calcualte_nb_of_priority_zones_in_path()
        self.calculate_path_cost()

    def calculate_path_cost(self) -> None:
        for zone in self.path[1:]:
            self.cost += zone.get_cost()

    def find_min_max_drones(self) -> int:
        min: int = self.path[0].metadata.max_drones

        for zone in self.path[1:]:
            max_drones = zone.metadata.max_drones
            if max_drones < min:
                min = max_drones
        return min

    def add_drones_until_equalize(
            self, drones: list[Drone], next_path_cost: int) -> int:
        max_drones = self.find_min_max_drones()
        print("max_drones min ", max_drones)

        for (idx, drone) in enumerate(drones):
            if self.cost + (idx + 1 - max_drones) >= next_path_cost:
                return idx

            self.drones.append(drone)

        return len(drones)

    def calcualte_nb_of_priority_zones_in_path(self):
        for zone in self.path:
            if zone.metadata.state == ZoneState.PRIORITY:
                self.nb_of_priority_zones += 1
