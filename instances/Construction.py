import math
import random
from typing import List

from instances.LocalSearch import hillclimbing, find_first_improvement_2Opt
from instances.Route import RouteObject
from instances.Trucks import Vehicle
from instances.Utils import Instance, Solution, next_fit_heuristic, compute_total_demand, compute_distances, routeCost, \
    temporaryRouteCost, delete_empty_routes


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


def ouralgorithm(instance: Instance, listOfRoutes: List[RouteObject], function):
    listOfCustomerList_sweep = list(map(lambda x: x.customer_list, listOfRoutes))
    distancesSweep = compute_distances(listOfCustomerList_sweep, instance)
    bestDistance = distancesSweep
    bestIteration = -1
    bestSolution_LoCL = listOfCustomerList_sweep.copy()  # copy solution from sweep as starting solution

    print(f"Sweep solution: {listOfCustomerList_sweep}")

    print(list(map(lambda x: x.current_cost, listOfRoutes)))  # printing out costs of the routes after sweep but before costs are assigned [0,0,0,0...]
    for r in listOfRoutes:
        r.current_cost = routeCost(r, instance)
    print(list(map(lambda x: x.current_cost, listOfRoutes)))  # printing out costs of the routes after sweep after costs are assigned

    """START OF THE BIG BAD LOOP
    ------------------------------------------------------------------------------------------------------------------
    ------------------------------------------------------------------------------------------------------------------
    """
    for iteration in range(100):  # run our algorithm 10 times
        print(f"New iteration__________{iteration}")
        print(f"Routes at start of it {iteration}:          {bestSolution_LoCL}")

        # START OF DESTRUCTION PHASE
        # Random Removal Operation
        numberOfRemoved = random.randint(round(0.1 * (len(instance.q) - 1)), round(0.5 * (len(instance.q) - 1)))  # generate number customers to be removed
        listOfRemoved = random.sample(range(1, len(instance.q)), numberOfRemoved)  # generate customers to be removed, starting from 1 so depo isn't getting deleted
        listAfterDestruction = []
        for i in range(len(bestSolution_LoCL)):
            element = [e for e in bestSolution_LoCL[i] if e not in listOfRemoved]
            listAfterDestruction.append(element)
        print(f"Customers to be removed: {listOfRemoved}")
        print(f"Routes after destruction:         {listAfterDestruction}")

        # positionInListAfterDestruction = 0
        # for l in listOfRoutes:
        #     l.customer_list = listAfterDestruction[positionInListAfterDestruction]
        #     positionInListAfterDestruction += 1
        for i in range(len(listAfterDestruction)):
            listOfRoutes[i].customer_list = listAfterDestruction[i]
        print(f"Routes objects after destruction: {list(map(lambda x: x.customer_list, listOfRoutes))}")
        # END OF DESTRUCTION PHASE. Result - listAfterDestruction and listOfRemoved

        # # START OF INSERTION PHASE
        # # Cheapest Global Insertion Operation
        # listOfPayloads = []
        # for i in instance.Q:
        #     listOfPayloads.append(i.payload_kg)
        # while len(listOfRemoved) > 0:
        #     bestInsertionDistance = 10e10  # very big number
        #     bestPosition = 0
        #     bestCustomer = 0
        #     for customerIndex in range(len(listOfRemoved)):  # iterating over list of removed customers
        #         for i in range(len(listAfterDestruction)):  # iterating over routes in listAfterDestruction
        #             for j in range(len(listAfterDestruction[i]) - 1):  # iterating over positions in a route
        #                 keyNegative = (listAfterDestruction[i][j], listAfterDestruction[i][j + 1])
        #                 key1Positive = (listAfterDestruction[i][j], listOfRemoved[customerIndex])
        #                 key2Positive = (listOfRemoved[customerIndex], listAfterDestruction[i][j + 1])
        #                 insertionDistance = instance.d[key1Positive] + instance.d[key2Positive] - instance.d[keyNegative]  # calculation of insertion distance
        #                 if (insertionDistance < bestInsertionDistance) & (compute_total_demand(listAfterDestruction[i], instance) + instance.q[listOfRemoved[customerIndex]] < max(listOfPayloads)):  # & feasibilityCheck(instance, listAfterDestruction, listOfRemoved, customerIndex, i)
        #                     bestInsertionDistance = insertionDistance
        #                     bestPosition = (i, j + 1)
        #                     bestCustomer = listOfRemoved[customerIndex]
        #     if bestInsertionDistance != 10e10:
        #         listAfterDestruction[bestPosition[0]].insert(bestPosition[1], bestCustomer)  # insert bestCustomer to the best feasible route for them
        #     else:
        #         bestCustomer = listOfRemoved[0]  # if there are no feasible routes then open a new route and place 1st customer there
        #         listToAppend = [0, bestCustomer, 0]
        #         listAfterDestruction.append(listToAppend)
        #     listOfRemoved.remove(bestCustomer)  # delete current bestCustomer from a list of removed customers
        # print(f"Routes after insertion: {listAfterDestruction}")
        # # END OF INSERTION PHASE

        # START OF THE COST INSERTION PHASE
        while len(listOfRemoved) > 0:

            bestInsertionCost = 10e10  # very big number
            bestPosition = (0, 0)
            bestCustomer = 0

            for r in listOfRoutes:
                r.current_cost = routeCost(r, instance)
            # print(list(map(lambda x: x.current_cost, listOfRoutes)))  # printing out costs of the routes after i-th loop of the insertion phase

            for customerIndex in range(len(listOfRemoved)):  # iterating over list of removed customers
                for i in listOfRoutes:  # iterating over routes in listOfRoutes
                    for j in range(len(i.customer_list) - 1):  # iterating over positions in a route
                        costWithout = i.current_cost
                        # everything is ok until this line
                        temporaryCustomerList = i.customer_list.copy()
                        temporaryCustomerList.insert(j + 1, listOfRemoved[customerIndex])
                        costWith = temporaryRouteCost(temporaryCustomerList, i.vehicle, instance)
                        insertionCost = costWith - costWithout
                        if (insertionCost < bestInsertionCost) & (compute_total_demand(i.customer_list, instance) + instance.q[listOfRemoved[customerIndex]] < i.vehicle.payload_kg): # & feasibilityCheck(instance, listAfterDestruction, listOfRemoved, customerIndex, i)
                            bestInsertionCost = insertionCost
                            bestPosition = (i, j + 1)
                            bestCustomer = listOfRemoved[customerIndex]

            if bestInsertionCost != 10e10:
                # listAfterDestruction[bestPosition[0]].insert(bestPosition[1], bestCustomer)  # insert bestCustomer to the best feasible route for them
                bestPosition[0].customer_list.insert(bestPosition[1], bestCustomer)
            else:
                bestCustomer = listOfRemoved[0]  # if there are no feasible routes then open a new route and place 1st customer there
                listToAppend = [0, bestCustomer, 0]
                listOfRoutes.append(RouteObject(listToAppend, Vehicle("MercedesBenzAtego", "Paris", "999999")))
            listOfRemoved.remove(bestCustomer)  # delete current bestCustomer from a list of removed customers

        print(f"Routes objects after insertion:   {list(map(lambda x: x.customer_list, listOfRoutes))}")
        # END OF THE COST INSERTION PHASE

        # DELETING EMPTY ROUTES
        """ Deleting routes currently causes out-of-bound-errors because we use List[List] and List[Route] in parallel"""
        # listOfRoutes = delete_empty_routes(listOfRoutes)
        # print(f"Routes objects no empty routes:   {list(map(lambda x: x.customer_list, listOfRoutes))}")

        # START OF OPTIMIZATION PHASE
        listAfterInsertion = []
        for r in listOfRoutes:
            listAfterInsertion.append(r.customer_list)

        listAfterOptimization = hillclimbing(listAfterInsertion, instance, function)
        print(f"Routes after optimization:        {listAfterOptimization}")
        # END OF OPTIMIZATION PHASE. Result - listAfterDestruction

        # START OF VEHICLE SWAP PHASE

        # END OF VEHICLE SWAP PHASE


        # START OF ACCEPTANCE PHASE
        distancesOurAlgorythm = compute_distances(listAfterOptimization, instance)
        if distancesOurAlgorythm < bestDistance:
            bestDistance = distancesOurAlgorythm
            bestSolution_LoCL = listAfterOptimization
            bestIteration = iteration
        print(f"Total distance of the current iteration: {distancesOurAlgorythm}")
        print(f"The best distance: {bestDistance}")
        print(f"The best iteration: {bestIteration}")



        # END OF ACCEPTANCE PHASE
    if distancesSweep < bestDistance:
        print(f"Sweep Heuristic distance: {distancesSweep}, ourAlgorithm distance: {bestDistance}. Sweep is better")
    elif distancesSweep == bestDistance:
        print(
            f"Sweep Heuristic distance: {distancesSweep}, ourAlgorithm distance: {bestDistance}. Algorithms are equal")
    else:
        print(f"Sweep Heuristic distance: {distancesSweep}, ourAlgorithm distance: {bestDistance}. ourAlgorithm is better")
    return bestSolution_LoCL



# def truckAssigning(solution: Solution, instance: Instance):  # currently hardcoded
#     # listOfPayloads = []
#     # for i in instance.Q:
#     #     listOfPayloads.append(i.capacity)
#     assignedTrucks = []
#     licencePlate = 000000
#     for i in solution:
#         check = compute_total_demand(i, instance)
#         if 2800 > check > 905:
#             assignedTrucks.append(MercedesBenzAtego(licencePlate))
#         elif check > 883:
#             assignedTrucks.append(StreetScooterWORKL(licencePlate))
#         elif check > 720:
#             assignedTrucks.append(VWTransporter(licencePlate))
#         elif check > 670:
#             assignedTrucks.append(StreetScooterWORK(licencePlate))
#         elif check > 100:
#             assignedTrucks.append(VWCaddypanelvan(licencePlate))
#         else:
#             assignedTrucks.append(DouzeV2ECargoBike(licencePlate))
#         licencePlate += 1
#
#     return assignedTrucks
# # END OF TRUCK ASSIGNING PHASE