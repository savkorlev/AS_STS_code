import math
import random
from typing import List

from instances.LocalSearch import hillclimbing, find_first_improvement_2Opt
from instances.Plot import plotTSP
from instances.Route import RouteObject
from instances.Trucks import Vehicle
from instances.Utils import Instance, Solution, next_fit_heuristic, compute_total_demand, compute_distances, routeCost, \
    temporaryRouteCost, delete_empty_routes, vehicle_assignment, solution_cost


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




def ouralgorithm(instance: Instance, initialSolution: List[RouteObject], function, listOfInitialVehicles: List[Vehicle], coordinates_int: List): # coordinates_int is only for matplot
    # LoCL = List of Customer List
    # bestSolution_LoCL = list(map(lambda x: x.customer_list, listOfRoutes)) # copy solution from sweep as starting solution
    listOfRoutes = initialSolution.copy()

    bestSolution = listOfRoutes.copy()
    # distancesSweep = compute_distances(list(map(lambda x: x.customer_list, listOfRoutes)), instance)
    # bestDistance = distancesSweep
    bestCost = solution_cost(listOfRoutes, instance)
    bestIteration = -1

    print(f"Sweep solution: {list(map(lambda x: x.customer_list, listOfRoutes))}") # printing out customer lists after sweep
    print(f"Route costs:    {list(map(lambda x: x.current_cost, listOfRoutes))}")  # printing out costs of the routes after sweep after costs are assigned

    """START OF THE LOOP
    ------------------------------------------------------------------------------------------------------------------
    ------------------------------------------------------------------------------------------------------------------
    """
    for iteration in range(100):  # run our algorithm 10 times
        print(f"New iteration__________{iteration}")
        print(f"Routes at start of iter {iteration}:        {list(map(lambda x: x.customer_list, listOfRoutes))}")

        # START OF DESTRUCTION PHASE
        bestSolution_beforeDestruction = list(map(lambda x: x.customer_list, bestSolution))

        # Random Removal Operation
        numberOfRemoved = random.randint(round(0.1 * (len(instance.q) - 1)), round(0.5 * (len(instance.q) - 1)))  # generate number customers to be removed
        listOfRemoved = random.sample(range(1, len(instance.q)), numberOfRemoved)  # generate customers to be removed, starting from 1 so depo isn't getting deleted
        listOfRemoved.sort()  # for better readability during debugging """ somehow this does not seem to work """
        listAfterDestruction = []
        for i in range(len(bestSolution_beforeDestruction)):
            element = [e for e in bestSolution_beforeDestruction[i] if e not in listOfRemoved]
            listAfterDestruction.append(element)
        print(f"Customers to be removed: {listOfRemoved}")
        print(f"Routes after destruction:         {listAfterDestruction}")

        """ I encountered a bug here where after destructing we have more routes than before, and the order of the routes is changed. After destruction has 11 routes, before had 10.
        data at bug:
        
        New iteration__________8
Routes at start of it 8:          [[0, 24, 15, 17, 6, x29, 0], [0, 20, 39, 37, 14, 9, 0], [0, 3, 31, 18, 10, 23, 19, 0], [0, 25, 36, 22, 13, 21, 11, 0], [0, 5, 38, 26, 12, 7, 33, 0], [0, 30, 16, 8, 1, 32, 0], [0, 2, 0], [0, 35, 34, 0], [0, 28, 4, 0], [0, 27, 0]]
Customers to be removed: [35, 14, 29, 30, 34, 28, 31, 1, 17, 19, 32, 2, 7, 26, 18, 36]
Routes after destruction:         [[0, 24, 15, 6, 0], [0, 3, 10, 23, 0], [0, 5, 38, 12, 33, 0], [0, 25, 22, 13, 21, 11, 0], [0, 16, 8, 0], [0, 0], [0, 0], [0, 20, 39, 37, 9, 0], [0, 0], [0, 4, 0], [0, 27, 0]]

New iteration__________4
Routes at start of iter 4:        [[0, 30, 16, 17, 15, 8, 13, 0], [0, 11, 21, 22, 2, 35, 36, 0], [0, 3, 18, 26, 6, 38, 33, 0], [0, 37, 14, 34, 23, 19, 0], [0, 24, 12, 39, 1, 32, 0], [0, 25, 10, 0], [0, 29, 0], [0, 31, 0], [0, 9, 4, 27, 0], [0, 28, 7, 0], [0, 5, 0], [0, 20, 0]]
Customers to be removed: [20, 23, 32, 34, 39]
Routes after destruction:         [[0, 30, 16, 17, 15, 8, 13, 0], [0, 0], [0, 3, 18, 26, 6, 38, 33, 0], [0, 11, 21, 22, 2, 35, 36, 0], [0, 24, 12, 1, 0], [0, 31, 0], [0, 37, 14, 19, 0], [0, 9, 4, 27, 0], [0, 28, 7, 0], [0, 5, 0], [0, 25, 10, 0], [0, 29, 0], [0, 0]]
        
        """

        for i in range(len(listAfterDestruction)):
            listOfRoutes[i].customer_list = listAfterDestruction[i].copy()  # turn list after destruction back into listOfRoutes
        print(f"Route objects after destruction:  {list(map(lambda x: x.customer_list, listOfRoutes))}")

        # START OF THE COST INSERTION PHASE
        while len(listOfRemoved) > 0:

            bestInsertionCost = 10e10  # very big number
            bestPosition = (0, 0)
            bestCustomer = 0

            for r in listOfRoutes:
                r.current_cost = routeCost(r, instance) # recalculate route cost after destruction
            # print(list(map(lambda x: x.current_cost, listOfRoutes)))  # printing out costs of the routes after i-th loop of the insertion phase

            for customerIndex in range(len(listOfRemoved)):  # iterating over list of removed customers
                for i in listOfRoutes:  # iterating over routes in listOfRoutes
                    for j in range(len(i.customer_list) - 1):  # iterating over positions in a route
                        costWithout = i.current_cost
                        temporaryCustomerList = i.customer_list.copy()
                        temporaryCustomerList.insert(j + 1, listOfRemoved[customerIndex])
                        costWith = temporaryRouteCost(temporaryCustomerList, i.vehicle, instance)
                        insertionCost = costWith - costWithout
                        if (insertionCost < bestInsertionCost) & (compute_total_demand(i.customer_list, instance) + instance.q[listOfRemoved[customerIndex]] < i.vehicle.payload_kg): # & feasibilityCheck(instance, listAfterDestruction, listOfRemoved, customerIndex, i)
                            bestInsertionCost = insertionCost
                            bestPosition = (i, j + 1)
                            bestCustomer = listOfRemoved[customerIndex]

            if bestInsertionCost != 10e10:
                bestPosition[0].customer_list.insert(bestPosition[1], bestCustomer) # insert bestCustomer to the best feasible route for them
            else:
                bestCustomer = listOfRemoved[0]  # if there are no feasible routes then open a new route and place 1st customer there
                listToAppend = [0, bestCustomer, 0]
                listOfRoutes.append(RouteObject(listToAppend, Vehicle("MercedesBenzAtego", "Paris", "999999")))  # create new route with dummy vehicle
            listOfRemoved.remove(bestCustomer)  # delete current bestCustomer from a list of removed customers

        print(f"Route objects after insertion:    {list(map(lambda x: x.customer_list, listOfRoutes))}")
        # END OF THE COST INSERTION PHASE

        # DELETING EMPTY ROUTES
        listOfRoutes = delete_empty_routes(listOfRoutes)
        print(f"Route objects no empty routes:    {list(map(lambda x: x.customer_list, listOfRoutes))}")


        # START OF OPTIMIZATION PHASE.
        listAfterOptimization = hillclimbing(list(map(lambda x: x.customer_list, listOfRoutes)), instance, function)
        for i in range(len(listAfterOptimization)):
            listOfRoutes[i].customer_list = listAfterOptimization[i].copy()

        print(f"Route objects after optimization: {list(map(lambda x: x.customer_list, listOfRoutes))}")
        # END OF OPTIMIZATION PHASE.

        # START OF VEHICLE SWAP PHASE
        vehicle_assignment(listOfRoutes, listOfInitialVehicles, instance) # def vehicle_assignment(list_of_routes: list[Route], initial_list_of_vehicles: List[Vehicle], instance: Instance):
        # END OF VEHICLE SWAP PHASE


        # START OF ACCEPTANCE PHASE
        costThisIteration = solution_cost(listOfRoutes, instance)
        if costThisIteration < bestCost:
            bestCost = costThisIteration
            bestSolution = listOfRoutes.copy()
            bestIteration = iteration
        print(f"Total cost of the current iteration: {costThisIteration}")
        print(f"The best known cost: {bestCost}")
        print(f"The best iteration: {bestIteration}")



        # distancesOurAlgorythm = compute_distances(listAfterOptimization, instance)
        # if distancesOurAlgorythm < bestDistance: # will be replaced by Sim Annealing
        #     bestDistance = distancesOurAlgorythm
        #     bestSolution_LoCL = listAfterOptimization
        #     bestIteration = iteration
        # print(f"Total distance of the current iteration: {distancesOurAlgorythm}")
        # print(f"The best distance: {bestDistance}")
        # print(f"The best iteration: {bestIteration}")

        # plotTSP(bestSolution_LoCL, coordinates_int) # use this if you want to plot after every iteration

    #     # END OF ACCEPTANCE PHASE
    # TODO switch the final output to cost
    # if distancesSweep < bestDistance:
    #     print(f"Sweep Heuristic distance: {distancesSweep}, ourAlgorithm distance: {bestDistance}. Sweep is better")
    # elif distancesSweep == bestDistance:
    #     print(
    #         f"Sweep Heuristic distance: {distancesSweep}, ourAlgorithm distance: {bestDistance}. Algorithms are equal")
    # else:
    #     print(f"Sweep Heuristic distance: {distancesSweep}, ourAlgorithm distance: {bestDistance}. ourAlgorithm is better")

    print(f"Finished after iteration {iteration}")
    return list(map(lambda x: x.customer_list, bestSolution))
    # return bestSolution_LoCL



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