from enum import Enum


class ParsingError(Exception):
    pass


class ZoneState(Enum):
    NORMAL = 0,
    PRIORITY = 1,
    RESTRICTED = 2,
    BLOCKED = 3,


class ZoneMetadata:
    def __init__(self, zone: ZoneState = ZoneState.NORMAL, color: str = "ESC[33m",
                 max_drones: int = 1) -> None:
        self.zone = zone
        self.color = color
        self.max_drones = max_drones

    @staticmethod
    def from_line(line: str) -> "ZoneMetadata":
        if not line:
            return ZoneMetadata()

        metadata = {}

        for data in line.split():
            data = data.split("=")
            if len(data) == 2:
                metadata[data[0]] = data[1]
            else:
                raise ParsingError(f"The metadata {data[0]} is not valid")

        return ZoneMetadata.from_dict(metadata)

    @staticmethod
    def from_dict(metadata: dict[str, str]) -> "ZoneMetadata":
        m = ZoneMetadata()

        for key in metadata:
            match key:
                case "zone":
                    m.zone = ZoneMetadata.set_zone(metadata[key])
                case "color":
                    m.color = metadata[key]
                case "max_drones":
                    try:
                        max_drones = int(metadata[key])
                        if max_drones < 0:
                            raise ParsingError("negative number not allowed")
                        m.max_drones = max_drones
                    except ValueError as e:
                        raise e
                case _:
                    raise ParsingError(f"The key {key} is not valid")

        return m

    @staticmethod
    def set_zone(zone_state: str) -> ZoneState:
        match zone_state.strip().lower():
            case "normal":
                return ZoneState.NORMAL
            case "priority":
                return ZoneState.PRIORITY
            case "restricted":
                return ZoneState.RESTRICTED
            case "blocked":
                return ZoneState.BLOCKED
            case _:
                raise ParsingError(
                    f"This is a not a valid zone state {zone_state}")


class ConnectionMetadata:
    def __init__(self, max_link_capacity: int = 1) -> None:
        self.max_link_capacity = max_link_capacity

    @staticmethod
    def from_line(line: str) -> "ConnectionMetadata":
        if not line:
            return ConnectionMetadata()

        data = line.split("=")
        if data[0].strip() != "max_link_capacity":
            raise ParsingError(f"the metadata {data[0]} doesn't exist")

        if len(data) == 2:
            try:
                max_link_capacity = int(data[1])

                if max_link_capacity < 0:
                    raise ParsingError("negatif value is not allowed")
            except ValueError as e:
                raise e
        else:
            raise ParsingError(f"The metadata {data[0]} is not valid")

        return ConnectionMetadata(max_link_capacity)


class Zone:
    def __init__(self, name: str, position: tuple[int, int],
                 metadata: ZoneMetadata | None, type_name: str = "", connections: list["Connection"] | None = None) -> None:
        self.name = name
        self.position = position
        self.metadata = metadata
        self.connections = connections if connections is not None else []
        self.type_name = type_name

    @staticmethod
    def from_line(line: str) -> "Zone":
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
            metadata_str = " ".join(strs[3:])

        metadata = ZoneMetadata.from_line(metadata_str)

        return Zone(name, position, metadata, type_name)


class Connection:
    def __init__(self, start: Zone, dest: Zone,
                 max_link_capacity: int = 1, type_name: str = "") -> None:
        self.start = start
        self.dest = dest
        self.max_link_capacity = max_link_capacity
        self.type_name = type_name

    @staticmethod
    def from_line(line: str, zones: dict[str, Zone]) -> "Connection":
        if not line:
            raise ParsingError("A empty line what")
        
        (type_name, _, strs) = line.partition(":")

        strs = strs.strip().split()

        zone_names = strs[0].split("-")

        if len(zone_names) == 1:
            raise ParsingError("This is not a valid connection")

        try:
            start = zones[zone_names[0]]
            dest = zones[zone_names[1]]
        except KeyError as e:
            raise e

        if len(strs) == 2:
            m = ConnectionMetadata.from_line(strs[1])
            return Connection(start, dest, m.max_link_capacity, type_name)

        return Connection(start, dest, type_name=type_name)

    # def is_valid_connection(self) -> bool:
    #     pass


class Parser():
    def __init__(self, file: str) -> None:
        self.file = file
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []

    # like a fsm
    # # all of this is pseudo code
    # def parse(self):
    #     # start
    #     if start:
    #         # check if the first line is nb drone
    #         # after start
    #     for line in lines:
    #         if line.startwith("hub: "):
    #             if len(self.connections) > 0:
    #                 raise ...
    #             zone = Zone.from_line()
    #             self.zones[zone.name] = zone
    #         if line.startwith("connection: ") and len(self.zones) > 0:
    #             if not len(self.zones):
    #                 raise ...
    #             self.connections.append(Connection.from_line())
    #     # join the connection with its zone
        # end

    # def is_valid_name(self) -> bool:
    #     pass
