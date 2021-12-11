import math
import random
from typing import List

from instances.LocalSearch import hillclimbing
from instances.Utils import Instance, Solution, next_fit_heuristic, compute_total_demand, compute_distances


def sweep_algorithm(instance: Instance) -> Solution:
    # sort the customers according to the sweep
    sorted_customers = sort_customers_by_sweep(instance)
    # assign them to routes (next fit)
    return next_fit_heuristic(sorted_customers, instance)


def random_sweep(instance: Instance) -> Solution:
    customer_list = sort_customers_by_sweep(instance)

    # emulate changing the starting angle by rotating the list of customers
    rotate = random.randint(0, instance.n - 1)
    customer_list = customer_list[rotate:] + customer_list[:rotate]

    # emulate changing the direction of the sweep by reversing the list of customers
    if random.randint(0, 1) == 1:
        customer_list.reverse()

    return next_fit_heuristic(customer_list, instance)


def sort_customers_by_sweep(instance: Instance) -> List[int]:
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


def ouralgorithm(instance: Instance, solution: Solution, function):
    # START OF DESTRUCTION PHASE
    numberOfRemoved = random.randint(round(0.1 * (len(instance.q) - 1)), round(0.5 * (len(instance.q) - 1)))  # generate number customers to be removed
    listOfRemoved = random.sample(range(1, len(instance.q)), numberOfRemoved)  # generate customers to be removed, starting from 1 so depo isn't getting deleted
    listAfterDestruction = []
    for i in range(len(solution)):
        element = [e for e in solution[i] if e not in listOfRemoved]
        listAfterDestruction.append(element)
    print(solution); print(listAfterDestruction); print(listOfRemoved)
    # END OF DESTRUCTION PHASE. Result - listAfterDestruction and listOfRemoved

    # START OF INSERTION PHASE
    while len(listOfRemoved) > 0:
        bestInsertionDistance = 10000
        bestPosition = 0
        bestCustomer = 0
        for customerIndex in range(len(listOfRemoved)):  # iterating over list of removed customers
            for i in range(len(listAfterDestruction)):  # iterating over routes in listAfterDestruction
                for j in range(len(listAfterDestruction[i]) - 1):  # iterating over positions in a route
                    keyNegative = (listAfterDestruction[i][j], listAfterDestruction[i][j + 1])
                    key1Positive = (listAfterDestruction[i][j], listOfRemoved[customerIndex])
                    key2Positive = (listOfRemoved[customerIndex], listAfterDestruction[i][j + 1])
                    insertionDistance = instance.d[key1Positive] + instance.d[key2Positive] - instance.d[keyNegative]  # calculation of insertion distance
                    if (insertionDistance < bestInsertionDistance) & (compute_total_demand(listAfterDestruction[i], instance) + instance.q[listOfRemoved[customerIndex]] < instance.Q):  # checking both conditions, first - lowest distance, second - total demand after insertion must be lower than our truck's capacity
                        bestInsertionDistance = insertionDistance
                        bestPosition = (i, j + 1)
                        bestCustomer = listOfRemoved[customerIndex]
        listAfterDestruction[bestPosition[0]].insert(bestPosition[1], bestCustomer)  # insert bestCustomer to the best feasible route for them
        listOfRemoved.remove(bestCustomer)  # delete current bestCustomer from a list of removed customers
    print(listAfterDestruction)
    # END OF INSERTION PHASE

    # START OF OPTIMIZATION PHASE
    listAfterOptimization = hillclimbing(listAfterDestruction, instance, function)
    return listAfterOptimization
    # END OF OPTIMIZATION PHASE. Result - listAfterDestruction


# START OF ACCEPTANCE PHASE
def checkForAcceptance(solutionSweep: Solution, solutionOur: Solution, instance: Instance):
    distancesSweep = compute_distances(solutionSweep, instance)
    distancesOurAlgorythm = compute_distances(solutionOur, instance)
    if distancesSweep < distancesOurAlgorythm:
        print(f"Sweep Heuristic distance: {distancesSweep}, ourAlgorithm distance: {distancesOurAlgorythm}. Sweep is better")
    elif distancesSweep == distancesOurAlgorythm:
        print(f"Sweep Heuristic distance: {distancesSweep}, ourAlgorithm distance: {distancesOurAlgorythm}. Algorithms are equal")
    else:
        print(f"Sweep Heuristic distance: {distancesSweep}, ourAlgorithm distance: {distancesOurAlgorythm}. ourAlgorithm is better")
# END OF ACCEPTANCE PHASE
# distance between (0 and 1) + (1 and 19) - (0 and 19)
# check for feasibility before insertion - now with capacity, distance later on (maybe check it after for loops if performance is poor)
# make a greedy code but comment everything
# check empty routes and create new routes
