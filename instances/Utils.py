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

        # algorithm will run until first of these conditions is met. Either iterations or time.
        self.max_iterations = 3000
        self.max_time = 5.0  # seconds

        self.init_temp = 0.9  # factor with which the solution of the 0. iteration is turned into first temperature -> ourAlgorithm()
        self.cooling = 0.95  # factor with which temperature is reduced after every instance  -> simulated_annealing()

        # set the initial weights for each operator
        self.init_weight_destroy_random = 50
        self.init_weight_destroy_expensive = 50
        self.init_weight_destroy_route = 50
        self.init_weight_insert_cheapest = 50
        self.init_weight_insert_regret = 25


        self.init_penalty = 5  # starting penalty costs in the 0. iteration -> penalty_cost()
        self.step_penalty = 1  # step by which penalty grows in every iteration -> penalty_cost()
        # TODO: Choose suitable penalty-factor. Maybe depending on max_iterations?

        self.penalty_cost_iteration_for_initialization = 0.75 * self.max_iterations   # setting this parameter correctly is very important for the initial solution.




Route = List[int]
Solution = List[Route]


# def next_fit_heuristic_naive(instance: Instance) -> Solution:
#     order = list(range(1, instance.n))
#     return next_fit_heuristic(order, instance)


# def compute_distances(solution: Solution, instance: Instance) -> float:
#     sum_distances = 0.0
#
#     for route in solution:
#         sum_distances += compute_distance(route, instance)
#
#     return sum_distances


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


# def is_feasible(solution: Solution, instance: Instance) -> bool:
#     """
#     checks whether a solution (list of routes) is feasible, i.e.,
#     all customers are visited exactly once and the maximum load capacity Q is never exceeded
#     :param solution: list of routes
#     :param instance: corresponding instance
#     :return: True if feasible, False otherwise
#     """5
#
#     listOfPayloads = []
#     for i in instance.Q:
#         listOfPayloads.append(i.payload_kg)
#
#     for route in solution:
#         load = compute_total_demand(route, instance)
#         if load > max(listOfPayloads):  # checking max capacity among the whole list
#             print(f"Error: load capacity is exceeded ({load} > {max(listOfPayloads)})")
#             return False
#
#     node_visited = [0] * instance.n
#     for route in solution:
#         for r_i in route:
#             node_visited[r_i] += 1
#
#     for v in range(1, instance.n):
#         if node_visited[v] != 1:
#             print(f"Error: node {v} has been visited {node_visited[v]} times")
#             return False
#
#     return True


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

""" I rewrote temporaryRouteCost to not create a RouteObject every time, but it did not improve calculation speed"""

def temporaryRouteCost(customer_list: Route, vehicle: Vehicle, instance: Instance, iteration: int, penalty_active=True) -> float:
    # distance
    distance = compute_distance(customer_list, instance)
    cost_km = distance * vehicle.costs_km

    # penalty
    cost_penalty = 0
    if penalty_active:  # checks if penalty_costs were enabled when calling the cost function
        cost_penalty = penalty_cost(customer_list, vehicle, instance, iteration, distance)

    cost = cost_km + cost_penalty
    return cost


def routeCost(routeObject: RouteObject, instance: Instance, iteration: int, penalty_active=True) -> float:
    # distance
    distance = compute_distance(routeObject.customer_list, instance)
    cost_km = distance * routeObject.vehicle.costs_km

    # penalty
    cost_penalty = 0
    if penalty_active:  # checks if penalty_costs were enabled when calling the cost function
        cost_penalty = penalty_cost(routeObject.customer_list, routeObject.vehicle, instance, iteration, distance)

    cost = cost_km + cost_penalty
    return cost

def penalty_cost(customer_list: list(), vehicle: Vehicle, instance: Instance, iteration: int, distance: float) -> float:
    iteration_penalty = instance.init_penalty + iteration * instance.step_penalty  # penalty in each iteration.

    # payload_kg
    constraint_kg = vehicle.payload_kg
    load_kg = compute_total_demand(customer_list, instance)
    overload_kg = compute_overload(constraint_kg, load_kg)
    cost_kg = overload_kg * iteration_penalty

    # range

    # combine
    penalty = cost_kg  # + all other penalized constraints

    # if penalty > 0:  # set the feasibility of the route by checking if penality > 0.
    #     routeObject.currently_feasible = False
    # else: routeObject.currently_feasible = True

    return penalty


""" temporaryRouteCost is used in some instances (e.g. customer insertion) where we want to test how expensive a 
Route will be after a change. Since we dont want to change the route itself, we call temporaryRouteCost() instead of
routeCost(). temporaryRouteCost then creates a tempRoute object and calls routeCost(). This means we only have to make
changes in routeCost, if we want to alter the way costs are calculated.
There is probably a way to have routeCost take either a RouteObject or (customer_list + Vehicle) and then decide what
to do depending on the arguments that got passed, but I'm not smart enough for that
- Christopher 2022-01-10
"""

# def temporaryRouteCost(customer_list: Route, vehicle: Vehicle, instance: Instance, iteration: int, penalty_active=True) -> float:
#     tempRoute = RouteObject(customer_list, vehicle)
#     cost = routeCost(tempRoute, instance, iteration, penalty_active)
#     return cost


# def routeCost(routeObject: RouteObject, instance: Instance, iteration: int, penalty_active=True) -> float:
#     # distance
#     cost_km = compute_distance(routeObject.customer_list, instance) * routeObject.vehicle.costs_km
#
#     # penalty
#     cost_penalty = 0
#     if penalty_active:  # checks if penalty_costs were enabled when calling the cost function
#         cost_penalty = penalty_cost(routeObject, instance, iteration)
#
#     cost = cost_km + cost_penalty
#     return cost


# def penalty_cost(routeObject: RouteObject, instance: Instance, iteration: int) -> float:
#     # TODO: Choose suitable penalty-factor.
#     iteration_penalty = 5 + iteration * 1  # penalty in each iteration.
#
#     # payload_kg
#     constraint_kg = routeObject.vehicle.payload_kg
#     load_kg = compute_total_demand(routeObject.customer_list, instance)
#     overload_kg = compute_overload(constraint_kg, load_kg)
#     cost_kg = overload_kg * iteration_penalty
#
#     # combine
#     penalty = cost_kg  # + all other penalized constraints
#
#     if penalty > 0:  # set the feasibility of the route by checking if penality > 0. TODO: Be careful if this is used for temp_costs (like for comparison in insertion)
#         routeObject.currently_feasible = False
#     else: routeObject.currently_feasible = True
#
#     return penalty


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