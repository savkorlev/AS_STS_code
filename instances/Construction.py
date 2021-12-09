import math
import random
from typing import List

from instances.Utils import Instance, Solution, next_fit_heuristic


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


def ourdistruction(solution: Solution):
    numberOfRemoved = random.randint(2, 10)                             # 10% out of 19 is ~ 2, 50% ~ 10
    listOfRemoved = random.sample(range(1, 19), numberOfRemoved)
    listAfterDestruction = []
    for i in range(len(solution)):
        element = [e for e in solution[i] if e not in listOfRemoved]
        listAfterDestruction.append(element)
    return [listAfterDestruction, listOfRemoved]

# testSolution = [[0, 19, 10, 18, 0], [0, 3, 5, 12, 0], [0, 6, 17, 7, 0], [0, 15, 16, 1, 0], [0, 13, 8, 11, 0], [0, 14, 4, 0], [0, 9, 2, 0]]
# numberOfRemoved = random.randint(2, 10)  # 10% out of 19 is ~ 2, 50% ~ 10
# listOfRemoved = random.sample(range(1, 19), numberOfRemoved)
# testOutput = []
# for i in range(len(testSolution)):
#     element = [e for e in testSolution[i] if e not in listOfRemoved]
#     testOutput.append(element)
# print(testSolution)