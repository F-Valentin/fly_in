from enum import Enum


class ZoneError(Exception):
    pass


class ZoneState(Enum):
    NORMAL = 0,
    PRIORITY = 1,
    RESTRICTED = 2,
    BLOCKED = 3,


class ZoneMetadata:
    def __init__(self, state: ZoneState = ZoneState.NORMAL, color: str = "ESC[33m",
                 max_drones: int = 1) -> None:
        self.state = state
        self.color = color
        self.max_drones = max_drones

    @staticmethod
    def from_line(line: str) -> "ZoneMetadata":
        if not line:
            return ZoneMetadata()

        metadata = {}
        line = line.strip("[]")

        for data in line.split():
            data = data.split("=")
            if len(data) == 2:
                metadata[data[0]] = data[1]
            else:
                raise ZoneError(f"The metadata {data[0]} is not valid")

        return ZoneMetadata.from_dict(metadata)

    @staticmethod
    def from_dict(metadata: dict[str, str]) -> "ZoneMetadata":
        m = ZoneMetadata()

        for key in metadata:
            match key:
                case "zone":
                    m.state = ZoneMetadata.set_state(metadata[key])
                case "color":
                    m.color = metadata[key]
                case "max_drones":
                    try:
                        max_drones = int(metadata[key])
                        if max_drones < 0:
                            raise ZoneError("negative number not allowed")
                        m.max_drones = max_drones
                    except ValueError as e:
                        raise e
                case _:
                    raise ZoneError(f"The key {key} is not valid")

        return m

    @staticmethod
    def set_state(zone_state: str) -> ZoneState:
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
                raise ZoneError(
                    f"This is a not a valid zone state {zone_state}")

    def __str__(self):
        return (
            f"zone_state: {self.state}, "
            f"color: {self.color}, "
            f"max_drones: {self.max_drones}"
        )


class Zone:

    def __init__(self, name: str, position: tuple[int, int],
                 metadata: ZoneMetadata, type_name: str = "", connections: list["Connection"] | None = None) -> None:
        self.name = name
        self.position = position
        self.metadata = metadata
        self.connections = connections if connections is not None else []
        self.type_name = type_name
        self.nb_drones = 0

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

    def add_connection(
            self, connections: list["Connection"], zones: dict[str, Zone]) -> None:
        from connection import Connection
        for connection in connections:
            if self.name == connection.start.name:
                self.connections.append(connection)
                dest = zones[connection.dest.name]
                dest.connections.append(
                    Connection(
                        dest,
                        self,
                        connection.max_link_capacity,
                        "connection"))

    def get_cost(self) -> int:
        match self.metadata.state:
            case ZoneState.NORMAL | ZoneState.PRIORITY:
                return 1
            case ZoneState.RESTRICTED:
                return 2
            case _: return 0

    def __str__(self):
        connections_str = ", ".join(
            connection.dest.name for connection in self.connections)
        return (
            f"name: {self.name}, "
            f"positon: {self.position}, "
            f"metadata: {self.metadata}, "
            f"connections: {connections_str}"
        )
