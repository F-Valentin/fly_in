from zone import Zone
from drone import Drone
from connection import Connection
from path import Path

class Simulation:
    def __init__(self, end_hub: Zone) -> None:
        self.turn: int = 0
        self.active_connections: list[Connection] = []
        self.end_hub: Zone = end_hub
        self.colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "reset": "\033[0m"
        }

    def get_connection(self, start: Zone, dest: Zone) -> Connection | None:
        for connection in start.connections:
            if connection.dest.name == dest.name:
                if len(connection.waiting_drone) < connection.max_link_capacity:
                    return connection
                break

        return None

    def _format_move(self, drone: Drone, start: Zone, dest: Zone) -> str:
        color_key = dest.metadata.color.lower()
        color_code = self.colors.get(color_key, "")
        reset = self.colors["reset"] if color_code else ""
        
        if dest.get_cost() > 1:
            display = f"D{drone.id}-{start.name}-{dest.name}"
        else:
            display = f"D{drone.id}-{dest.name}"
            
        return f"{color_code}{display}{reset}"

    def _process_arrivals(self, drones: list[Drone]) -> list[Drone]:
        finished_drones: list[Drone] = []

        for connection in self.active_connections:
            for drone in list(connection.waiting_drone):
                drone.waiting_turn -= 1

                if drone.waiting_turn <= 0:
                    dest = connection.dest

                    if dest.name == self.end_hub.name or dest.nb_drones < dest.metadata.max_drones:
                        drone.status = "move"
                        connection.waiting_drone.remove(drone)
                        dest.nb_drones += 1

                        if dest.name == self.end_hub.name:
                            finished_drones.append(drone)

        return finished_drones

    def _process_departures(self, drones: list[Drone]) -> list[str]:
        movements: list[str] = []
        for drone in drones:
            if len(drone.path) <= 1:
                print("error path len < 1")
                continue

            if drone.status == "waiting":
                continue
            
            start = drone.path[0]
            dest = drone.path[1]
            connection = self.get_connection(start, dest)

            if connection:
                if connection not in self.active_connections:
                    self.active_connections.append(connection)

                drone.waiting_turn = dest.get_cost()
                connection.waiting_drone.append(drone)
                drone.status = "waiting"
                
                movements.append(self._format_move(drone, start, dest))
                
                if start.nb_drones > 0:
                    start.nb_drones -= 1
                drone.path.pop(0)

        return movements

    def simulation(self, drones: list[Drone], paths: list[Path]) -> int:
        for path in paths:
            for drone in path.drones:
                drone.path.extend(path.path)

        while drones:
            finished = self._process_arrivals(drones)
            for d in finished:
                if d in drones:
                    drones.remove(d)

            if not drones:
                break

            moves = self._process_departures(drones)
            
            if moves:
                # print(" ".join(moves))
                print(f"{' '.join(moves)} # Turn {self.turn + 1}")
            
            self.turn += 1

        return self.turn