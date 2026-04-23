from enum import Enum
from zone import Zone
from connection import Connection


class ParsingError(Exception):
    pass


class Parser():
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.file = ""
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.data = {}

    def open_file(self) -> bool:
        try:
            with open(self.file_path) as f:
                self.file = f.readlines()
        except (FileNotFoundError, PermissionError) as e:
            print(e)
            return False
        return True

    def parse(self) -> dict:
        nb_drones = 0
        start_hub = False
        end_hub = False

        for line in self.file:
            line = line.strip()

            if line.startswith("#"):
                continue

            if line.startswith("nb_drones:"):
                if nb_drones != 0:
                    raise ParsingError("nb_drones already define")

                line = line.split(":")

                try:
                    nb_drones = int(line[1])
                    if nb_drones < 0:
                        raise ParsingError("negatif number not valid")
                except ValueError as e:
                    raise e

            elif (line.startswith("hub:") or line.startswith("start_hub:")
                  or line.startswith("end_hub:")):
                try:
                    zone = Zone.from_line(line)

                    if zone.name in self.zones:
                        raise ParsingError(
                            f"The hub {zone.name} already exist")

                    if zone.type_name == "start_hub":
                        if start_hub:
                            raise ParsingError("start hub already exist")
                        self.data["start_hub"] = zone
                        start_hub = True

                    elif zone.type_name == "end_hub":
                        if end_hub:
                            raise ParsingError("end hub already exist")
                        self.data["end_hub"] = zone
                        end_hub = True

                    self.zones[zone.name] = zone
                except (ValueError, ParsingError) as e:
                    raise e

            elif line.startswith("connection:"):
                try:
                    connection = Connection.from_line(line, self.zones)
                    self.connections.append(connection)
                except (ValueError, ParsingError) as e:
                    raise e

        if not nb_drones:
            raise ParsingError("nb_drones is missing")

        if not start_hub or not end_hub:
            raise ParsingError("start hub or end hub is/are missing")

        for zone in self.zones.values():
            zone.add_connection(self.connections, self.zones)

        self.data["nb_drones"] = nb_drones
        self.data["zones"] = self.zones

        return self.data


def main():
    file_path = [
        "../maps/easy/01_linear_path.txt",
        # "maps/easy/02_simple_fork.txt",
        # "maps/easy/03_basic_capacity.txt",
        # "maps/medium/01_dead_end_trap.txt",
        # "maps/medium/02_circular_loop.txt",
        # "maps/medium/03_priority_puzzle.txt",
        # "maps/hard/01_maze_nightmare.txt",
        # "maps/hard/02_capacity_hell.txt",
        # "maps/hard/03_ultimate_challenge.txt",
    ]
    for fp in file_path:
        print(fp)
        parser = Parser(fp)
        try:
            parser.open_file()
            data = parser.parse()
            zones = data["zones"]
            for zone in zones.values():
                print(zone)
        except Exception as e:
            print(e)


main()
