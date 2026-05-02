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

        for (idx, drone) in enumerate(drones):
            if self.cost + (idx - max_drones) >= next_path_cost:
                return idx

            self.drones.append(drone)

        return len(drones)
    
    @staticmethod
    def add_drones_to_paths(drones: list[Drone], paths: list[Path]) -> None:
        paths_len = len(paths)
        nb_drones_add = 0
        old_nb_drones_add  = 0

        if paths_len == 1:
            for drone in drones:
                paths[0].drones.append(drone)
            return
            
        for (i, path) in enumerate(paths):
            if i + 1 < paths_len:
                old_nb_drones_add = nb_drones_add
                nb_drones_add += path.add_drones_until_equalize(drones[nb_drones_add:], paths[i + 1].cost)
            else:
                d = drones[nb_drones_add:]
                d_len = len(d) - old_nb_drones_add
                for i in range(d_len):
                    path.drones.append(d[i])
                    nb_drones_add += 1
        
        i = 0
        if nb_drones_add == len(drones):
            return

        for drone in drones[nb_drones_add:]:
            paths[i].drones.append(drone)
            i = (i + 1) % paths_len



    def calcualte_nb_of_priority_zones_in_path(self):
        for zone in self.path:
            if zone.metadata.state == ZoneState.PRIORITY:
                self.nb_of_priority_zones += 1
