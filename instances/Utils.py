from typing import List, Dict, Tuple

from instances import Trucks


class Instance:
    """
    n : int
        number of nodes in total
    Q : List
        list of trucks
    q : List[int]
        list of customer demands
    d : Dict[Tuple[int, int], float]
        list of distances
    coordinates : List[Tuple[int, int]]
        list of customer coordinates
    """

    n: int
    Q: List
    q: List[int]
    d: Dict[Tuple, float]
    coordinates: List[Tuple[int, int]]

    def __init__(self, n: int, Q: List, q: List[int], d: Dict[Tuple[int, int], float],
                 coordinates: List[Tuple[int, int]]):
        self.n = n
        self.Q = Q
        self.q = q
        self.d = d
        self.coordinates = coordinates


Route = List[int]
Solution = List[Route]


def next_fit_heuristic_naive(instance: Instance) -> Solution:
    order = list(range(1, instance.n))
    return next_fit_heuristic(order, instance)


def next_fit_heuristic(customer_list: List[int], instance: Instance) -> Solution:
    routes: Solution = list()
    open_route = [0]
    open_route_capacity_used = 0

    listOfPayloads = []
    for i in instance.Q:
        listOfPayloads.append(i.capacity)

    for c in customer_list:
        demand = instance.q[c]

        if open_route_capacity_used + demand <= 900:  # 900 is a made-up number
            # assign customer to route
            open_route.append(c)
            open_route_capacity_used += demand

        else:
            # close active route
            open_route.append(0)
            routes.append(open_route)

            # open new route and assign customer
            open_route = [0, c]
            open_route_capacity_used = demand

    # close active route
    open_route.append(0)
    routes.append(open_route)  # close the last route

    return routes


def compute_distances(solution: Solution, instance: Instance) -> float:
    sum_distances = 0.0

    for route in solution:
        sum_distances += compute_distance(route, instance)

    return sum_distances


def compute_distance(route: Route, instance: Instance) -> float:
    sum_distances = 0.0

    # route: [0,1,2,3,4,0]
    #   (i-1)-^ ^-i
    for i in range(1, len(route)):
        key = (route[i - 1], route[i])
        sum_distances += instance.d[key]

    return sum_distances


def compute_total_demand(route: List[int], instance: Instance) -> int:
    sum_demands = 0
    for n in route:
        sum_demands += instance.q[n]

    return sum_demands


def is_feasible(solution: Solution, instance: Instance) -> bool:
    """
    checks whether a solution (list of routes) is feasible, i.e.,
    all customers are visited exactly once and the maximum load capacity Q is never exceeded

    :param solution: list of routes
    :param instance: corresponding instance
    :return: True if feasible, False otherwise
    """

    listOfPayloads = []
    for i in instance.Q:
        listOfPayloads.append(i.capacity)

    for route in solution:
        load = compute_total_demand(route, instance)
        if load > max(listOfPayloads):  # checking max capacity among the whole list
            print(f"Error: load capacity is exceeded ({load} > {max(listOfPayloads)})")
            return False

    node_visited = [0] * instance.n
    for route in solution:
        for r_i in route:
            node_visited[r_i] += 1

    for v in range(1, instance.n):
        if node_visited[v] != 1:
            print(f"Error: node {v} has been visited {node_visited[v]} times")
            return False

    return True


# def feasibilityCheck(instance: Instance, listAfterDestruction: List[int], listOfRemoved: List[int], customerIndex: int, i: int):
#
#     listOfPayloads = []
#     for i in instance.Q:
#         listOfPayloads.append(i.capacity)
#
#     if compute_total_demand(listAfterDestruction[i], instance) + instance.q[listOfRemoved[customerIndex]] < max(listOfPayloads):  # checking both conditions, first - lowest distance, second - total demand after insertion must be lower than our truck's capacity
#         return True
#
#     return False
# (compute_total_demand(listAfterDestruction[i], instance) + instance.q[listOfRemoved[customerIndex]] < max(listOfPayloads)):  # checking both conditions, first - lowest distance, second - total demand after insertion must be lower than our truck's capacity # add feasibility check

def routeCost(vehicleType, route: Route, instance: Instance):
    cost = compute_distance(route, instance) * vehicleType.costs_km
    return cost
