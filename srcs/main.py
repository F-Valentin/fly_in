from parser import Parser
from solver import Solver
from path import Path
from drone import Drone
from simulation import Simulation


def main():
    file_path = [
        "../maps/easy/01_linear_path.txt",
        # "../maps/easy/02_simple_fork.txt",
        # "../maps/easy/03_basic_capacity.txt",
        # "../maps/medium/01_dead_end_trap.txt",
        # "../maps/medium/02_circular_loop.txt",
        # "../maps/medium/03_priority_puzzle.txt",
        # "maps/hard/01_maze_nightmare.txt",
        # "maps/hard/02_capacity_hell.txt",
        # "../maps/hard/03_ultimate_challenge.txt",
        # "../maps/challenger/01_the_impossible_dream.txt",
    ]
    for fp in file_path:
        parser = Parser(fp)
        try:

            if not parser.open_file():
                print("fail")
                return
            data = parser.parse()
            zones = data["zones"]
        except Exception as e:
            print(e)
            return

    start = data["start_hub"]
    end = data["end_hub"]

    paths: list[Path] = []
    all_paths = Solver.dfs(start, end)

    drones = Drone.create_drones(data["nb_drones"])
    print(drones)
    for path in all_paths:
        paths.append(Path(path))

    paths.sort(key=lambda p: p.cost)

    Path.add_drones_to_paths(drones, paths)

    for path in paths:
        print(path.drones)
    simulation = Simulation(end)

    turn = simulation.simulation(drones, paths)
    print("turn ", turn)
     # for drone in drones:
    #     print(drone)
    # nb_of_drones = path.add_drones_until_equalize(drones, s_path.cost)
    # Drone.remove_drones_in_order(nb_of_drones, drones)
    # print()
    # for drone in drones:
    #     print(drone)


main()
