from typing import List, Dict, Tuple

from instances import Trucks
from instances.Route import RouteObject
from instances.Trucks import Vehicle


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
        listOfPayloads.append(i.payload_kg)

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

def compute_distances_objects(solution: Solution, instance: Instance) -> float:
    sum_distances = 0.0

    for route in solution:
        sum_distances += compute_distance(route.customer_list, instance)

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
        listOfPayloads.append(i.payload_kg)

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

def routeCost(routeObject: RouteObject, instance: Instance):
    cost = compute_distance(routeObject.customer_list, instance) * routeObject.vehicle.costs_km
    return cost

def temporaryRouteCost(route: Route, vehicle: Vehicle, instance: Instance):
    cost = compute_distance(route, instance) * vehicle.costs_km
    return cost


def delete_empty_routes(list_of_routes: list[Route]) -> list[Route]:
    no_empty_routes = list_of_routes.copy()
    for r in list_of_routes:
        if len(r.customer_list) < 3:
            no_empty_routes.remove(r)
    return no_empty_routes

def vehicle_assignment(list_of_routes: list[Route], initial_list_of_vehicles: List[Vehicle], instance: Instance):
    list_of_routes.sort(key=lambda x: x.current_cost, reverse=True)  # orders routes by cost descending
    # print(f"Routes costs descending: {list(map(lambda x: x.current_cost, listOfRoutes))}")
    list_of_available_vehicles = initial_list_of_vehicles.copy()
    dummyAtego = Vehicle("MercedesBenzAtego", "Paris", "999999")

    for r in list_of_routes:  # check all routes. Before this they should be ordered by their costs descending
        # costBefore = r.current_cost
        best_vehicle = dummyAtego
        best_cost = 10e10
        for v in list_of_available_vehicles:  # check all available vehicles. This list should get shorter while we progress, because the best vehicles will be removed from it
            if compute_total_demand(r.customer_list, instance) < v.payload_kg:  # feasibility check over payload. can be removed once we have penalty costs
                tempCost = temporaryRouteCost(r.customer_list, v, instance)  # cost with the checked vehicle
                if tempCost < best_cost:
                    best_vehicle = v
                    best_cost = tempCost
        r.vehicle = best_vehicle  # assign the bestVehicle to the route
        list_of_available_vehicles.remove(best_vehicle)  # remove the bestVehicle from available.
        r.current_cost = routeCost(r, instance)  # update the route cost
        print(f"Route cost after Vehicle Assignment: route {r}, vehicle {r.vehicle.type} {r.vehicle.plateNr}, cost: {r.current_cost}, demand {compute_total_demand(r.customer_list, instance)}")