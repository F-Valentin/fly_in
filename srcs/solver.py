from drone import Drone
from zone import Zone, ZoneState
from connection import Connection


class Solver:
    def __init__(self) -> None:
        pass

    @staticmethod
    def dfs_rec(source: Zone, dest: Zone,
                path: list[Zone], visited_zone: set[str], all_paths: list[list[Zone]]):

        # take care about max_link_capacity = 0 to remove useless path
        path.append(source)

        if source.metadata.state == ZoneState.BLOCKED:
            return

        if source.name == dest.name:
            all_paths.append(path.copy())
            return

        visited_zone.add(source.name)
        for connection in source.connections:
            if connection.dest.name not in visited_zone:
                Solver.dfs_rec(
                    connection.dest,
                    dest,
                    path,
                    visited_zone,
                    all_paths)
                path.pop()
        visited_zone.remove(source.name)

    @staticmethod
    def dfs(start: Zone, dest: Zone) -> list[list[Zone]]:
        visited_zone: set[str] = set()
        all_paths: list[list[Zone]] = []

        Solver.dfs_rec(start, dest, [], visited_zone, all_paths)
        return all_paths
