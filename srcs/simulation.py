from zone import Zone
from drone import Drone
from connection import Connection
from path import Path


class Simulation:
    def __init__(self, end_hub: Zone) -> None:
        self.turn = 0
        self.connections = []
        self.end_hub: Zone = end_hub

    def get_connection(self, start: Zone, dest: Zone) -> Connection | None:
        for connection in start.connections:
            if connection.dest.name == dest.name:
                if len(connection.waiting_drone) < connection.max_link_capacity:
                    return connection

        return None

    def depart(self, drones: list[Drone]) -> None:
        print("depart")
        for drone in drones:
            if len(drone.path) <= 1:
                print("error path len < 1")
                return

            if drone.status == "waiting":
                continue
            
            print("Drone id: ", drone.id)
            start = drone.path[0]
            print("start zone: ", start)
            dest = drone.path[1]
            print("dest zone: ", dest)

            connection = self.get_connection(start, dest)
            if connection:
                if connection not in self.connections:
                    self.connections.append(connection)

                drone.waiting_turn = dest.get_cost()
                connection.waiting_drone.append(drone)
                drone.path.pop(0)
                drone.status = "waiting"

                if start.nb_drones > 0:
                    start.nb_drones -= 1
            else:
                print("turn ", self.turn)
                print("no connection")

    def arrive(self) -> list[Drone]:
        finished_drones: list[Drone] = []

        for connection in self.connections:
            for (idx, drone) in enumerate(connection.waiting_drone):
                drone.waiting_turn -= 1

                if drone.waiting_turn <= 0:
                    if connection.dest == self.end_hub:
                        finished_drones.append(drone)

                    dest = connection.dest
                    if (dest.nb_drones < dest.metadata.max_drones or dest.name ==
                            self.end_hub.name):
                        drone.status = "move"
                        connection.waiting_drone.pop(idx)
                        connection.dest.nb_drones += 1

        return finished_drones

    def simulation(self, drones: list[Drone], paths: list[Path]) -> int:
        for path in paths:
            for drone in path.drones:
                drone.path.extend(path.path)

        while drones:
            if self.turn == 4:
                break
            finished_drones = self.arrive()

            for drone in finished_drones:
                print("remove drone")
                drones.remove(drone)
            
            # print(self.connections)

            self.depart(drones)
            self.turn += 1

        return self.turn

    # def add_drone_to_connection(self, drone: Drone, connection: Connection):
    #     connection.waiting_drone.append(drone)
    #     if connection not in self.connections:
    #         self.connections.append(connection)

    # def simulation(self, drones: list[Drone], end_hub: Zone):
    #     end_drones = []
    #     while drones:
    #         for drone in end_drones:
    #             drones.remove(drone)
    #         for drone in drones:
    #             for connection in self.connections:
    #                 dest = connection.dest
    #                 for d in connection.waiting_drone:
    #                     if dest.name == end_hub.name:
    #                         d.status = ""
    #                         connection.waiting_drone.pop(0)
    #                     elif dest.nb_drones < dest.metadata.max_drones:
    #                         dest.nb_drones += 1
    #                         d.status = ""
    #                         connection.waiting_drone.pop(0)
    #                     else:
    #                         d.status = "waiting"

    #             if drone.status == "waiting":
    #                 continue
    #             start = drone.path[0]

    #             if start.name == end_hub.name:
    #                 end_drones.append(drone)
    #             else:
    #                 dest = drone.path[1]
    #                 for connection in start.connections:
    #                     if connection.dest.name == dest.name:
    #                         if len(connection.waiting_drone) < connection.max_link_capacity or dest.name == end_hub.name:
    #                             self.add_drone_to_connection(drone, connection)
    #                             zone = drone.path.pop(0)
    #                             if zone.nb_drones > 0:
    #                                 zone.nb_drones -= 1
    #                         break
    #         self.turn += 1
