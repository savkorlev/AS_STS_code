import copy
import random
import numpy as np
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


# def next_fit_heuristic_naive(instance: Instance) -> Solution:
#     order = list(range(1, instance.n))
#     return next_fit_heuristic(order, instance)


def next_fit_heuristic(all_customers: List[int], instance: Instance, initialVehicles: List[Vehicle]) -> list():

    """ penalty_cost_dummy_iteration sets the iteration that gives us the penalty cost for deciding if it is cheaper
    to add a new route or to add to the last open route.
    If this is chosen too high will only create feasible routes (if possible) and tends to overload the last vehicle available.
    Setting it too low only creates infeasible routes.
    A good idea seems to be to set it to 75% of maxIteration"""
    penalty_cost_dummy_iteration = 75  # setting this parameter correctly is very important for the initial solution.

    listOfRoutes = []
    availableVehicles = copy.deepcopy(initialVehicles)

    randomVehicle = random.choice(availableVehicles)
    listOfRoutes.append(RouteObject([0, 0], randomVehicle))
    availableVehicles.remove(randomVehicle)

    for current_customer in all_customers:
        last_route = listOfRoutes[len(listOfRoutes) - 1]  # len - 1 gives us the last position
        last_position = len(last_route.customer_list) - 1  # len - 1 gives us the last position

        temp_route = last_route.customer_list.copy()
        temp_route.insert(last_position, current_customer)
        cost_with = temporaryRouteCost(temp_route, last_route.vehicle, instance, penalty_cost_dummy_iteration, True)  # set iteration to something where it will already have reasonable penalties
        cost_without = temporaryRouteCost(last_route.customer_list, last_route.vehicle, instance, penalty_cost_dummy_iteration, True)
        last_route_cost = cost_with - cost_without


        if len(availableVehicles) > 0:  # only try to pick a new vehicle if we still have vehicles available
            randomVehicle = random.choice(availableVehicles)
            new_route_cost = temporaryRouteCost([0, current_customer, 0], randomVehicle, instance, penalty_cost_dummy_iteration, True)
            if last_route_cost <= new_route_cost:
                last_route.customer_list.insert(last_position, current_customer)
            else:
                new_route = RouteObject([0, current_customer, 0], randomVehicle)
                listOfRoutes.append(new_route)
                availableVehicles.remove(randomVehicle)
        else:
            last_route.customer_list.insert(last_position, current_customer)

    return listOfRoutes


""" old next_fit_heuristic built by Christopher. Can only create feasible routes."""
# def next_fit_heuristic(all_customers: List[int], instance: Instance, initialVehicles: List[Vehicle]) -> Solution:
#     routes: Solution = list()
#     open_route = [0]
#     open_route_capacity_used = 0
#     listOfRoutes = []
#
#     availiableVehicles = copy.deepcopy(initialVehicles)
#
#     randomVehicle = random.choice(availiableVehicles)
#
#     for c in all_customers:
#         demand = instance.q[c]
#         while (open_route_capacity_used == 0) & (demand > randomVehicle.payload_kg):  # makes sure we only start if we have a vehicle that can fit the customer
#             randomVehicle = random.choice(availiableVehicles)
#
#         if open_route_capacity_used + demand <= randomVehicle.payload_kg: #random.uniform(100, 2400):  # 900 is a made-up number
#             # assign customer to route
#             open_route.append(c)
#             open_route_capacity_used += demand
#
#         else:
#             # close active route
#             open_route.append(0)
#             newRoute = RouteObject(open_route, randomVehicle)
#             newRoute.current_cost = routeCost(newRoute, instance, 0, True)
#             listOfRoutes.append(newRoute)
#
#             availiableVehicles.remove(randomVehicle)
#
#             # open new route and assign customer
#             randomVehicle = random.choice(availiableVehicles)
#             while demand > randomVehicle.payload_kg:  # makes sure we only start if we have a vehicle that can fit the customer
#                 randomVehicle = random.choice(availiableVehicles) # This can lead to an infinite loop, if we only have vehicles left that are smaller than the customers left.
#             open_route = [0, c]
#             open_route_capacity_used = demand
#
#     # close active route
#     open_route.append(0)
#     newRoute = RouteObject(open_route, randomVehicle)
#     newRoute.current_cost = routeCost(newRoute, instance, 0, True)
#     listOfRoutes.append(newRoute)  # close the last route
#
#     return listOfRoutes

""" old next_fit_heuristic as used in life-coding """
# def next_fit_heuristic(customer_list: List[int], instance: Instance) -> Solution:
#     routes: Solution = list()
#     open_route = [0]
#     open_route_capacity_used = 0
#
#     listOfPayloads = []
#     for i in instance.Q:
#         listOfPayloads.append(i.payload_kg)
#
#     for c in customer_list:
#         demand = instance.q[c]
#
#         if open_route_capacity_used + demand <= random.uniform(100, 2400):  # 900 is a made-up number
#             # assign customer to route
#             open_route.append(c)
#             open_route_capacity_used += demand
#
#         else:
#             # close active route
#             open_route.append(0)
#             routes.append(open_route)
#
#             # open new route and assign customer
#             open_route = [0, c]
#             open_route_capacity_used = demand
#
#     # close active route
#     open_route.append(0)
#     routes.append(open_route)  # close the last route
#
#     return routes


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

def solution_cost(listOfRoutes: List[Route], instance: Instance, iteration: int, penalty_active=True) -> float:
    solutionCost = 0
    for r in listOfRoutes:
        solutionCost = solutionCost + routeCost(r, instance, iteration, penalty_active)
    return solutionCost


""" temporaryRouteCost is used in some instances (e.g. customer insertion) where we want to test how expensive a 
Route will be after a change. Since we dont want to change the route itself, we call temporaryRouteCost() instead of
routeCost(). temporaryRouteCost then creates a tempRoute object and calls routeCost(). This means we only have to make
changes in routeCost, if we want to alter the way costs are calculated.
There is probably a way to have routeCost take either a RouteObject or (customer_list + Vehicle) and then decide what
to do depending on the arguments that got passed, but I'm not smart enough for that
- Christopher 2022-01-10
"""
def temporaryRouteCost(customer_list: Route, vehicle: Vehicle, instance: Instance, iteration: int, penalty_active=True) -> float:
    tempRoute = RouteObject(customer_list, vehicle)
    cost = routeCost(tempRoute, instance, iteration, penalty_active)
    return cost


def routeCost(routeObject: RouteObject, instance: Instance, iteration: int, penalty_active=True) -> float:
    # distance
    cost_km = compute_distance(routeObject.customer_list, instance) * routeObject.vehicle.costs_km

    # penalty
    cost_penalty = 0
    if penalty_active:  # checks if penalty_costs were enabled when calling the cost function
        cost_penalty = penalty_cost(routeObject, instance, iteration)

    cost = cost_km + cost_penalty
    return cost


def penalty_cost(routeObject: RouteObject, instance: Instance, iteration: int) -> float:
    # TODO: Choose suitable penalty-factor.
    iteration_penalty = 5 + iteration * 1  # penalty in each iteration.

    # payload_kg
    constraint_kg = routeObject.vehicle.payload_kg
    load_kg = compute_total_demand(routeObject.customer_list, instance)
    overload_kg = compute_overload(constraint_kg, load_kg)
    cost_kg = overload_kg * iteration_penalty

    # combine
    penalty = cost_kg  # + all other penalized constraints

    if penalty > 0:  # set the feasibility of the route by checking if penality > 0. TODO: Be careful if this is used for temp_costs (like for comparison in insertion)
        routeObject.currently_feasible = False
    else: routeObject.currently_feasible = True

    return penalty


def compute_overload(constraint: int, load: int) -> float:
    # Overload factor can be changed to our will. Probably should get smthing from literature
    overload_factor = (max(load - constraint, 0) / constraint)# ** 2  # we normalize the factor by the constraint (to not punish more because values are higher), then we square to punish bigger overloads much more
    return overload_factor


def delete_empty_routes(list_of_routes: list[Route]) -> list[Route]:
    no_empty_routes = list_of_routes.copy()
    for r in list_of_routes:
        if len(r.customer_list) < 3:
            no_empty_routes.remove(r)
    return no_empty_routes


def vehicle_assignment(list_of_routes: list[Route], initial_list_of_vehicles: List[Vehicle], instance: Instance, iteration=0, penalty_active=True) -> List[Vehicle]:
    list_of_routes.sort(key=lambda x: x.current_cost, reverse=True)  # orders routes by cost descending # TODO: We can quickly become adaptive by not always starting with the most expensive route
    # print(f"Routes costs descending: {list(map(lambda x: x.current_cost, listOfRoutes))}")
    list_of_available_vehicles = initial_list_of_vehicles.copy()
    dummyAtego = Vehicle("MercedesBenzAtego", "Paris", "999999")

    counter = 0
    for r in list_of_routes:  # check all routes. Before this they should be ordered by their costs descending
        counter += 1
        # costBefore = r.current_cost
        best_vehicle = dummyAtego
        best_cost = 10e10
        for v in list_of_available_vehicles:  # check all available vehicles. This list should get shorter while we progress, because the best vehicles will be removed from it
            # if compute_total_demand(r.customer_list, instance) < v.payload_kg:  # feasibility check over payload. can be removed once we have penalty costs
            r.vehicle = v
            tempCost = routeCost(r, instance, iteration, penalty_active)  # cost with the checked vehicle
            if tempCost < best_cost:
                best_vehicle = v
                best_cost = tempCost
        r.vehicle = best_vehicle  # assign the bestVehicle to the route
        list_of_available_vehicles.remove(best_vehicle)  # remove the bestVehicle from available.
        r.current_cost = routeCost(r, instance, iteration, penalty_active)  # update the route cost
        print(f"Route cost after Vehicle Assignment: route {counter} , vehicle {r.vehicle.type} {r.vehicle.plateNr}, cost: {r.current_cost:.2f}, demand {compute_total_demand(r.customer_list, instance)}, customerCount: {len(r.customer_list)-2}, feasible: {r.currently_feasible}")
    return list_of_available_vehicles