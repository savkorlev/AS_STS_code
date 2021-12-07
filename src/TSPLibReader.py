####
# Read file in the format of TSPLIP instances for CVRPs
# returns a dict with
# "n" .. number of nodes
# "capacity" .. transport capacity per vehicle
# "nodes" .. a list of {'id': int, 'name': string, type: 'depot'|'customer, 'x': float, 'y': float, 'demand': int },
#   containing the index (starting with 0), the name of the node (id in the instance file),
#   the coordinates (x,y) and the demand. All files of this benchmark set start with the depot at 0 and are
#   sorted by name.
def read(path):
    nodes = list()
    with open(path, "r") as file:
        lines = file.read().splitlines()
        # DIMENSION: 32
        n = int(lines[3].rsplit(":")[1])
        # CAPACITY: 100
        capacity = int(lines[5].rsplit(":")[1])

    return {'n': n, 'capacity': capacity}
