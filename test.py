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
        line = line.strip("[]")

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

    def add_connection(
            self, connections: list[Connection], zones: dict[str, Zone]) -> None:
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
