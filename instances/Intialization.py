import copy
import math
import random

from instances.Route import RouteObject
from instances.Trucks import Vehicle
from instances.Utils import Instance, temporaryRouteCost


def next_fit_heuristic(all_customers: list[int], instance: Instance, initialVehicles: list[Vehicle]) -> list():

    """ penalty_cost_iteration_for_initialization sets the iteration that gives us the penalty cost for deciding if it is cheaper
    to add a new route or to add to the last open route.
    If this is chosen too high will only create feasible routes (if possible) and tends to overload the last vehicle available.
    Setting it too low only creates infeasible routes.
    A good idea seems to be to set it to 75% of maxIteration"""

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
        cost_with = temporaryRouteCost(temp_route, last_route.vehicle, instance, instance.penalty_cost_iteration_for_initialization, True)  # set iteration to something where it will already have reasonable penalties
        cost_without = temporaryRouteCost(last_route.customer_list, last_route.vehicle, instance, instance.penalty_cost_iteration_for_initialization, True)
        last_route_cost = cost_with - cost_without


        if len(availableVehicles) > 0:  # only try to pick a new vehicle if we still have vehicles available
            randomVehicle = random.choice(availableVehicles)
            new_route_cost = temporaryRouteCost([0, current_customer, 0], randomVehicle, instance, instance.penalty_cost_iteration_for_initialization, True)
            if last_route_cost <= new_route_cost:
                last_route.customer_list.insert(last_position, current_customer)
            else:
                new_route = RouteObject([0, current_customer, 0], randomVehicle)
                listOfRoutes.append(new_route)
                availableVehicles.remove(randomVehicle)
        else:
            last_route.customer_list.insert(last_position, current_customer)

    return listOfRoutes


def random_sweep(instance: Instance, initialVehicles: list[Vehicle]) -> list[RouteObject]:
    customer_list = sort_customers_by_sweep(instance)

    # emulate changing the starting angle by rotating the list of customers
    rotate = random.randint(0, instance.n - 1)
    customer_list = customer_list[rotate:] + customer_list[:rotate]

    # emulate changing the direction of the sweep by reversing the list of customers
    if random.randint(0, 1) == 1:
        customer_list.reverse()

    return next_fit_heuristic(customer_list, instance, initialVehicles)

# def sweep_algorithm(instance: Instance) -> Solution:
#     # sort the customers according to the sweep
#     sorted_customers = sort_customers_by_sweep(instance)
#     # assign them to routes (next fit)
#     return next_fit_heuristic(sorted_customers, instance)


def sort_customers_by_sweep(instance: Instance) -> list[int]:
    """
    sorts the customer visits by their angle in a polar coordinate system with the depot at its center.
    To break ties, the distance from the depot is used, then the id of the node itself (which is unique).
    :param instance: corresponding instance
    :return: list of ordered customers sorted by sweeping
    """

    center_x, center_y = instance.coordinates[0]

    customers_angles = []
    for i in range(1, instance.n):
        node_x, node_y = instance.coordinates[i]
        angle = math.atan2(node_y - center_y, node_x - center_x)
        if angle < 0:
            angle += 2.0 * math.pi

        # Update: let be more expressive here and use a dict with named keys
        customers_angles.append({'id': i, 'angle': angle, 'distance': instance.d[0, i]})

    # Update: it's possibility that the order is not clearly defined, so we need break ties in the sorting
    #  (two customers might have the same angle). We introduce the distance to the depot as the second feature
    #  to be sorted against, with the id as a last resort (they are unique).
    #  Tuples are naturally sorted by the first element first, and so on.
    #  We exploit that and provide such a tuple as a key to the sort function
    #
    # before: customers_angles.sort(key=lambda entry: entry[1])

    customers_angles.sort(key=lambda entry: (entry['angle'], entry['distance'], entry['id']))

    sorted_customers = []
    for entry in customers_angles:
        sorted_customers.append(entry['id'])

    return sorted_customers


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
