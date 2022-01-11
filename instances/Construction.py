import datetime
import math
import os
import random
import copy
import sys
from typing import List

from instances.DestructionOps import random_removal, expensive_removal
from instances.InsertionOps import cheapest_insertion_iterative, regret_insertion
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


def random_sweep(instance: Instance, initialVehicles: List[Vehicle]) -> Solution:
    customer_list = sort_customers_by_sweep(instance)

    # emulate changing the starting angle by rotating the list of customers
    rotate = random.randint(0, instance.n - 1)
    customer_list = customer_list[rotate:] + customer_list[:rotate]

    # emulate changing the direction of the sweep by reversing the list of customers
    if random.randint(0, 1) == 1:
        customer_list.reverse()

    return next_fit_heuristic(customer_list, instance, initialVehicles)


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



#TODO: Check all copy operations
def ouralgorithm(instance: Instance, initialSolution: List[RouteObject], listOfInitialVehicles: List[Vehicle],
                 listOfInitAvailableVehicles: List[Vehicle], maxIterations: int, coordinates_int: List): # coordinates_int is only for matplot
    # START OF INITIALIZATION PHASE
    starttime = datetime.datetime.now()
    list_of_available_vehicles = copy.deepcopy(listOfInitAvailableVehicles)
    initialCost = solution_cost(initialSolution, instance, 0, False)  # saving the initial cost (only feasible costs) to compare in the end
    # setting the initial solution up so we can compare to it in acceptance phase
    bestSolution = initialSolution.copy()  # set the initial solution as the best solution (until acceptance check)
    bestIteration = -1 # used in acceptance check
    listImprovingIterations = []


    print(f"Sweep solution: {list(map(lambda x: x.customer_list, bestSolution))}") # printing out customer lists after sweep
    print(f"Route costs:    {list(map(lambda x: x.current_cost, bestSolution))}")  # printing out costs of the routes after sweep after costs are assigned
    # END OF INITIALIZATION PHASE
    # -------------------------------------------------------------------------------------------------------------
    # START OF THE LOOP
    for iteration in range(maxIterations):  # run our algorithm multiple times
        print(f"New iteration__________{iteration}")
        print(f"Routes at start of iter {iteration}:        {list(map(lambda x: x.customer_list, bestSolution))}")
        # -------------------------------------------------------------------------------------------------------------
        # START OF DESTRUCTION PHASE
        # bestSolution_beforeDestruction = list(map(lambda x: x.customer_list, bestSolution))
        listOfRoutes = copy.deepcopy(bestSolution)  # at the start of each iteration, set the list of routes to best known solution

        if random.uniform(0, 1) >= 0.2:  # pick a destroy operation
            # Random Removal Operation
            listOfRemoved = random_removal(instance)
            destroy_op_used = "random_removal"
        else:
            # Expensive Removal Operation
            listOfRemoved = expensive_removal(listOfRoutes, instance, iteration)
            destroy_op_used = "expensive_removal"

        listOfRemoved.sort()  # for better readability during debugging

        temp_listOfRemoved = listOfRemoved.copy()
        for r in listOfRoutes:
            for rc in temp_listOfRemoved:  # TODO: turn into while len(temp_listOfRemoved) > 0 loop
                if rc in r.customer_list:
                    r.customer_list.remove(rc)

                    # temp_listOfRemoved.remove(rc)  # causes a bug where customers dont get deleted TODO: Fix this bug

        print(f"Customers to be removed:          {listOfRemoved}")
        print(f"Routes after destruction:         {list(map(lambda x: x.customer_list, listOfRoutes))}")

        for r in listOfRoutes:
            r.current_cost = routeCost(r, instance, iteration, True)  # recalculate route cost after destruction
        # END OF DESTRUCTION PHASE
        #  -------------------------------------------------------------------------------------------------------------
        # START OF INSERTION PHASE
        if random.uniform(0, 1) >= 0.5:  # pick a destroy operation
            # cheapest insertion with new  after 1 customer is assigned
            cheapest_insertion_iterative(listOfRoutes, listOfRemoved, list_of_available_vehicles, instance, iteration)
            insert_op_used = "cheapest_insert"
        else:
            # regret insertion
            regret_insertion(listOfRoutes, listOfRemoved, list_of_available_vehicles, instance, iteration)
            insert_op_used = "regret_insert"

        print(f"Route objects after insertion:    {list(map(lambda x: x.customer_list, listOfRoutes))}")
        # END OF INSERTION PHASE
        # -------------------------------------------------------------------------------------------------------------
        # START OF OPTIMIZATION PHASE.
        # DELETING EMPTY ROUTES
        listOfRoutes = delete_empty_routes(listOfRoutes)
        print(f"Route objects no empty routes:    {list(map(lambda x: x.customer_list, listOfRoutes))}")

        # START OF LOCAL OPTIMIZATION 2-opt
        """ 2-opt currently optimizes for distance. Since it is inter-route, I am fine with this. - Christopher"""
        listAfterOptimization = hillclimbing(list(map(lambda x: x.customer_list, listOfRoutes)), instance, find_first_improvement_2Opt) #TODO remove function from ouralgorithm arguments, call 2-opt here directly
        for i in range(len(listAfterOptimization)):
            listOfRoutes[i].customer_list = listAfterOptimization[i].copy()  # put the optimized customer lists back into our RouteObjects
        print(f"Route objects after optimization: {list(map(lambda x: x.customer_list, listOfRoutes))}")
        # END OF LOCAL OPTIMIZATION 2-opt

        # START OF VEHICLE SWAP PHASE
        list_of_available_vehicles = vehicle_assignment(listOfRoutes, listOfInitialVehicles, instance) # def vehicle_assignment(list_of_routes: list[Route], initial_list_of_vehicles: List[Vehicle], instance: Instance):
        # END OF VEHICLE SWAP PHASE
        # END OF OPTIMIZATION PHASE.
        # -------------------------------------------------------------------------------------------------------------
        # START OF ACCEPTANCE PHASE

        # count customers
        customer_count = 0
        for r in listOfRoutes:
            customer_count += len(r.customer_list) - 2  # -2 because of two depots in each customer_list
        # if customer_count != 111: # this needs to be set to the exact amount of customers we have, and then it can be used to check if we lose/gain customers
        #     print(f"Error! Customer Count is: {customer_count}")
        #     os._exit()
        print(f"customer count check: {customer_count}")

        print(f"Destroy Operation used: {destroy_op_used}.")

        bestCost = solution_cost(bestSolution, instance, iteration, True)
        print(f"Best known cost before this iteration: {bestCost}")
        print(f"Best iteration before this one: {bestIteration}")
        costThisIteration = solution_cost(listOfRoutes, instance, iteration, True)
        if costThisIteration < bestCost:
            bestCost = costThisIteration
            bestSolution = listOfRoutes.copy()
            bestIteration = iteration
            listImprovingIterations.append((iteration, destroy_op_used, insert_op_used))
        print(f"Total cost of the current iteration: {costThisIteration}")
        print(f"Best known cost: {bestCost}")
        print(f"Best iteration: {bestIteration}\n")
        # plotTSP(bestSolution_LoCL, coordinates_int) # use this if you want to plot after every iteration
        # END OF ACCEPTANCE PHASE
    # -------------------------------------------------------------------------------------------------------------
    # END OF LOOP
    print(f"Finished after iteration {iteration}")

    improvement = 100 - ((bestCost / initialCost) * 100)
    imp_per_it = improvement / (iteration + 1)
    print(f"Initialization cost [feasible]: {initialCost:.2f}, ourAlgorithm cost: {bestCost:.2f}.")
    print(f"We improved by {improvement:.2f}%. Average improvement per iteration: {imp_per_it:.2f}%.")
    print(f"We improved in the following iterations: {listImprovingIterations}.")
    endtime = datetime.datetime.now()
    print(f"Length of the run: {endtime - starttime}.\n")
    print(str(endtime))

    return list(map(lambda x: x.customer_list, bestSolution))