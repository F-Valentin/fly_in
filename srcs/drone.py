from zone import Zone


class Drone:
    def __init__(self, id: int) -> None:
        self.id = id
        self.status = "move"
        self.waiting_turn = 0
        self.path: list[Zone] = []

    @staticmethod
    def create_drones(nb_of_drones: int = 1) -> list["Drone"]:
        drones: list[Drone] = []

        for i in range(0, nb_of_drones):
            drones.append(Drone(i))

        return drones

    @staticmethod
    def remove_drones_in_order(nb_of_drones: int, drones: list["Drone"]):
        new_drones = drones[nb_of_drones:]
        drones.clear()
        drones.extend(new_drones)

    def __str__(self):
        return f"drone_id: {self.id}"
