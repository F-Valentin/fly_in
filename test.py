from enum import Enum
from os import stat


s = "hub: roof2 6 2 [zone=priority color=green max_drones=2]"

s = s.split()

metadata_str = " ".join(s[4:])


print(metadata_str)

# s = s.strip("[]")

# strs = s.split()

# metadata = {}

# for m in strs:
#     m = m.split("=")
#     if len(m) == 2:
#         metadata[m[0]] = m[1]

# print(metadata)


# example

class ParsingError(Exception):
    pass

# replace with rgb color later on


class Color(Enum):
    RED = 0,
    BLUE = 1,
    GREEN = 2,
    WHITE = 3,


class ZoneState(Enum):
    NORMAL = 0,
    PRIORITY = 1,
    RESTRICTED = 2,
    BLOCKED = 3,


class Metadata:
    def __init__(self, zone: ZoneState = ZoneState.NORMAL, color: Color = Color.WHITE,
                 max_drones: int = 1) -> None:
        self.zone = zone
        self.color = color
        self.max_drones = max_drones

    @staticmethod
    def from_line(line: str) -> "Metadata":
        if not line:
            return Metadata()

        metadata = {}

        for data in line:
            data = data.split("=")
            if len(data) == 2:
                metadata[data[0]] = data[1]
            else:
                raise ParsingError(f"The metadata {data[0]} is not valid")

        return Metadata.from_dict(metadata)

    @staticmethod
    def from_dict(metadata: dict[str, str]) -> "Metadata":
        m = Metadata()

        for key in metadata:
            match key:
                case "zone":
                    m.zone = metadata[key]
                case "color":
                    m.color = metadata[key]
                case "max_drones":
                    m.max_drones = metadata[key]
                case _:
                    raise ParsingError(f"The key {key} is not valid")

        if not m.is_valid_metadata():
            raise ParsingError(f"This is not a valid metadata {metadata}")

        return m

    def is_valid_metadata(self) -> bool:
        pass


class Zone:
    def __init__(self, name: str, position: tuple[int, int],
                 metadata: Metadata | None, type_name: str = "", connections: list["Connection"] = []) -> None:
        self.name = name
        self.position = position
        self.metadata = metadata
        self.connections = connections
        self.type_name = type_name

    @staticmethod
    def from_line(line: str) -> "Zone":
        # Zone knows how to build itself from a line
        if not line:
            pass

        (type_name, _, strs) = line.partition(":")

        strs = strs.strip().split()
        name = strs[0]

        try:
            x = int(strs[1])
            y = int(strs[2])
        except ValueError as e:
            raise e

        position = (x, y)
        metadata_str = ""

        if len(strs) > 3:
            metadata_str = " ".join(s[4:])

        metadata = Metadata.from_line(metadata_str)

        return Zone(name, position, metadata, type_name)


class Connection:
    def __init__(self, start: Zone, dest: Zone,
                 max_lint_capacity: int = 1) -> None:
        self.start = start
        self.dest = dest
        self.max_lint_capacity = max_lint_capacity

    @staticmethod
    def from_line(line: str, zones: dict[str, Zone]) -> Connection:
        # Zone knows how to build itself from a line
        # find the corresponding zone name
        Connection()
        pass

    def is_valid_connection(self) -> bool:
        pass


class Parser():
    def __init__(self, file: str) -> None:
        self.file = file
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []

    # like a fsm
    # all of this is pseudo code
    def parse(self):
        # start
        if start:
            # check if the first line is nb drone
            # after start
        for line in lines:
            if line.startwith("hub: "):
                if len(self.connections) > 0:
                    raise ...
                zone = Zone.from_line()
                self.zones[zone.name] = zone
            if line.startwith("connection: ") and len(self.zones) > 0:
                if not len(self.zones):
                    raise ...
                self.connections.append(Connection.from_line())
        # join the connection with its zone
        # end

    def is_valid_name(self) -> bool:
        pass
