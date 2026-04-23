from zone import Zone


class ConnectionError(Exception):
    pass


class ConnectionMetadata:
    def __init__(self, max_link_capacity: int = 1) -> None:
        self.max_link_capacity = max_link_capacity

    @staticmethod
    def from_line(line: str) -> "ConnectionMetadata":
        if not line:
            return ConnectionMetadata()

        data = line.split("=")
        if data[0].strip() != "max_link_capacity":
            raise ConnectionError(f"the metadata {data[0]} doesn't exist")

        if len(data) == 2:
            try:
                max_link_capacity = int(data[1])

                if max_link_capacity < 0:
                    raise ConnectionError("negatif value is not allowed")
            except ValueError as e:
                raise e
        else:
            raise ConnectionError(f"The metadata {data[0]} is not valid")

        return ConnectionMetadata(max_link_capacity)


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
            raise ConnectionError("A empty line what")

        (type_name, _, strs) = line.partition(":")

        strs = strs.strip().split()

        zone_names = strs[0].split("-")

        if len(zone_names) == 1:
            raise ConnectionError("This is not a valid connection")

        try:
            start = zones[zone_names[0]]
            dest = zones[zone_names[1]]
        except KeyError as e:
            raise e

        if len(strs) == 2:
            m = ConnectionMetadata.from_line(strs[1])
            return Connection(start, dest, m.max_link_capacity, type_name)

        return Connection(start, dest, type_name=type_name)

    def __str__(self):
        return (
            f"start: {self.start.name}, "
            f"dest: {self.dest.name}, "
            f"max_link_capicity: {self.max_link_capacity}, "
        )

    # def is_valid_connection(self) -> bool:
    #     pass
