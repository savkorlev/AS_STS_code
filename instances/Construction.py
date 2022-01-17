import datetime
import math
import os
import random
import copy
import sys
import time
from typing import List

from instances.DestructionOps import random_removal, expensive_removal, route_removal
from instances.InsertionOps import cheapest_insertion_iterative, regret_insertion
from instances.LocalSearch import hillclimbing, find_first_improvement_2Opt, vnd, find_first_improvement_relocate, \
    find_best_improvement_2Opt
from instances.Plot import plotTSP
from instances.Route import RouteObject
from instances.Trucks import Vehicle
from instances.Utils import Instance, Solution, compute_total_demand, routeCost, \
    temporaryRouteCost, delete_empty_routes, vehicle_assignment, solution_cost, simulated_annealing


#TODO: Check all copy operations
def ouralgorithm(instance: Instance, initialSolution: List[RouteObject], listOfInitialVehicles: List[Vehicle],
                 listOfInitAvailableVehicles: List[Vehicle], coordinates_int=[]): # coordinates_int is only for matplot
    # START OF INITIALIZATION PHASE
    starttime = datetime.datetime.now()
    list_of_available_vehicles = copy.deepcopy(listOfInitAvailableVehicles)
    # setting the initial solution up so we can compare to it in acceptance phase
    bestSolution = copy.deepcopy(initialSolution)  # set the initial solution as the best solution (until acceptance check)
    bestIteration = -1 # used in acceptance check

    # setting up weights, counters and lists for adaptive LNS and generating reports after algorithm finishes
    weight_destroy_random = instance.init_weight_destroy_random  # set initial weight for operation
    counter_destroy_random_imp = 0
    counter_destroy_random_rej = 0
    weight_destroy_expensive = instance.init_weight_destroy_expensive
    counter_destroy_expensive_imp = 0
    counter_destroy_expensive_rej = 0
    weight_destroy_route = instance.init_weight_destroy_route
    counter_destroy_route_imp = 0
    counter_destroy_route_rej = 0

    weight_insert_cheapest = instance.init_weight_insert_cheapest
    counter_insert_cheapest_imp = 0
    counter_insert_cheapest_rej = 0
    weight_insert_regret = instance.init_weight_insert_regret
    counter_insert_regret_imp = 0
    counter_insert_regret_rej = 0

    listImprovingIterations = []  # collects all iterations where we found an improvement

    # setting up counter to check how long we had no improvement
    counter_iterations_no_improvement = 0
    listFallbackIterations = []

    # set up parameters of simulated annealing
    currentSolution = copy.deepcopy(initialSolution)
    currentCost = solution_cost(initialSolution, instance, iteration=0, penalty_active=True)
    temperature = instance.init_temp * currentCost #  current cost is used to calculate initial temperature
    accept_time = 0

    print(f"Sweep solution: {list(map(lambda x: x.customer_list, bestSolution))}") # printing out customer lists after sweep
    print(f"Route costs:    {list(map(lambda x: x.current_cost, bestSolution))}")  # printing out costs of the routes after sweep after costs are assigned
    # END OF INITIALIZATION PHASE
    # -------------------------------------------------------------------------------------------------------------
    # START OF THE LOOP
    iteration = 0  # iterations are counted up at the start of the loop, so we start with 0 to have the first iteration = 1
    perf_starttime = time.perf_counter()  # starts the timer for our maxTime. Does not include the initialization. This is ok since the sweep is very short.
    time_so_far = 0.0

    while time_so_far < instance.max_time and iteration < instance.max_iterations:  # run until either maxIterations or maxTime is reached. Will do 1 last loop after maxTime.
        iteration += 1  # count up the iterations

        print(f"New iteration__________{iteration}")
        print(f"Routes at start of iteration:     {list(map(lambda x: x.customer_list, bestSolution))}")
        # -------------------------------------------------------------------------------------------------------------
        # START OF DESTRUCTION PHASE
        # bestSolution_beforeDestruction = list(map(lambda x: x.customer_list, bestSolution))
        listOfRoutes = copy.deepcopy(
            currentSolution)  # at the start of each iteration, set the list of routes to current known solution

        destroy_ops = ['random_removal', 'expensive_removal', 'route_removal']
        destroy_weights = [weight_destroy_random, weight_destroy_expensive, weight_destroy_route]
        destroy_op_used_list = random.choices(destroy_ops,
                                              weights=destroy_weights)  # chooses an option from a weighed list
        destroy_op_used = destroy_op_used_list[0]  # because the choices-operator returns a list

        if destroy_op_used == 'random_removal':  # pick a destroy operation
            listOfRemoved = random_removal(instance)
        elif destroy_op_used == 'expensive_removal':
            listOfRemoved = expensive_removal(listOfRoutes, instance, iteration)
        elif destroy_op_used == 'route_removal':
            listOfRemoved = route_removal(listOfRoutes)

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
        # if random.uniform(0, 1) >= 0.5:  # pick a destroy operation
        #     # cheapest insertion with new  after 1 customer is assigned
        #     cheapest_insertion_iterative(listOfRoutes, listOfRemoved, list_of_available_vehicles, instance, iteration)
        #     insert_op_used = "cheapest_insert"
        # else:
        #     # regret insertion
        #     regret_insertion(listOfRoutes, listOfRemoved, list_of_available_vehicles, instance, iteration)
        #     insert_op_used = "regret_insert"

        insert_ops = ['cheapest_insert', 'regret_insert']
        insert_weights = [weight_insert_cheapest, weight_insert_regret]
        insert_op_used_list = random.choices(insert_ops,
                                             weights=insert_weights)  # chooses an option from a weighed list
        insert_op_used = insert_op_used_list[0]  # because the choices-operator returns a list

        if insert_op_used == 'cheapest_insert':  # pick a destroy operation
            cheapest_insertion_iterative(listOfRoutes, listOfRemoved, list_of_available_vehicles, instance,
                                         iteration)
        elif insert_op_used == 'regret_insert':
            regret_insertion(listOfRoutes, listOfRemoved, list_of_available_vehicles, instance, iteration)

        print(f"Route objects after insertion:    {list(map(lambda x: x.customer_list, listOfRoutes))}")
        # END OF INSERTION PHASE
        # -------------------------------------------------------------------------------------------------------------
        # START OF OPTIMIZATION PHASE.
        # DELETING EMPTY ROUTES
        listOfRoutes = delete_empty_routes(listOfRoutes)
        print(f"Route objects no empty routes:    {list(map(lambda x: x.customer_list, listOfRoutes))}")

        # START OF LOCAL OPTIMIZATION 2-opt
        """ 2-opt currently optimizes for distance. Since it is inter-route, I am fine with this. - Christopher"""
        local_search_function = find_best_improvement_2Opt
        # if random.uniform(0, 1) > 0.3:
        #     local_search_function = find_first_improvement_2Opt
        # else:
        #     local_search_function = find_first_improvement_relocate

        listAfterOptimization = hillclimbing(list(map(lambda x: x.customer_list, listOfRoutes)), instance,
                                             local_search_function)
        for i in range(len(listAfterOptimization)):
            listOfRoutes[i].customer_list = listAfterOptimization[
                i].copy()  # put the optimized customer lists back into our RouteObjects
        print(f"Route objects after optimization: {list(map(lambda x: x.customer_list, listOfRoutes))}")
        # END OF LOCAL OPTIMIZATION 2-opt

        # START OF VEHICLE SWAP PHASE
        list_of_available_vehicles = vehicle_assignment(listOfRoutes, listOfInitialVehicles,
                                                        instance)  # def vehicle_assignment(list_of_routes: list[Route], initial_list_of_vehicles: List[Vehicle], instance: Instance):
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
        ## costThisIteration = solution_cost(listOfRoutes, instance, iteration, True)
        accept, costThisIteration, temperature = simulated_annealing(instance, currentSolution, listOfRoutes, temperature,
                                                                     iteration)
        accept_time += accept
        if accept:
            currentSolution = listOfRoutes
        if costThisIteration < bestCost:  # only if we find a BETTER solution, does not depend on acceptance. todo: revise this
            bestCost = costThisIteration
            bestSolution = copy.deepcopy(listOfRoutes)
            bestIteration = iteration
            listImprovingIterations.append((iteration, destroy_op_used, insert_op_used))
            counter_iterations_no_improvement = 0  # reset the counter

            if destroy_op_used == 'random_removal':
                weight_destroy_random = min(200, weight_destroy_random + iteration)
                counter_destroy_random_imp += 1
            elif destroy_op_used == 'expensive_removal':
                weight_destroy_expensive = min(200, weight_destroy_expensive + iteration)
                counter_destroy_expensive_imp += 1
            elif destroy_op_used == 'route_removal':
                weight_destroy_route = min(200, weight_destroy_random + iteration)
                counter_destroy_route_imp += 1

            if insert_op_used == 'cheapest_insert':
                weight_insert_cheapest = min(200, weight_insert_cheapest + iteration)
                counter_insert_cheapest_imp += 1
            elif insert_op_used == 'regret_insert':
                weight_insert_regret = min(200, weight_insert_regret + iteration)
                counter_insert_regret_imp += 1

        else:  # if we dont find a better solution solution:
            counter_iterations_no_improvement += 1

            if destroy_op_used == 'random_removal':  # pick a destroy operation
                weight_destroy_random = max(10, weight_destroy_random - 1)
                counter_destroy_random_rej += 1
            elif destroy_op_used == 'expensive_removal':
                weight_destroy_expensive = max(10, weight_destroy_expensive - 1)
                counter_destroy_expensive_rej += 1
            elif destroy_op_used == 'route_removal':  # pick a destroy operation
                weight_destroy_route = max(10, weight_destroy_route - 1)
                counter_destroy_route_rej += 1

            if insert_op_used == 'cheapest_insert':  # pick a destroy operation
                weight_insert_cheapest = max(10, weight_insert_cheapest - 1)
                counter_insert_cheapest_rej += 1
            elif insert_op_used == 'regret_insert':
                weight_insert_regret = max(10, weight_insert_regret - 1)
                counter_insert_regret_rej += 1

            if counter_iterations_no_improvement >= instance.max_iterations_no_improvement:  # if we cant find an improvement for very long, go back to the best known solution
                currentSolution = copy.deepcopy(bestSolution)
                counter_iterations_no_improvement = 0
                listFallbackIterations.append((iteration, costThisIteration, bestCost))

        print(f"Total cost of the current iteration: {costThisIteration}")
        print(f"Best known cost: {bestCost}")
        print(f"Best iteration: {bestIteration}, iterations without improvement: {counter_iterations_no_improvement}\n")
        # plotTSP(bestSolution_LoCL, coordinates_int) # use this if you want to plot after every iteration

        time_so_far = time.perf_counter() - perf_starttime  # update time for maxTime
        # END OF ACCEPTANCE PHASE
    # -------------------------------------------------------------------------------------------------------------
    # END OF LOOP
    print(f"random_removal stats: improvements: {counter_destroy_random_imp}, rejected: {counter_destroy_random_rej}")
    print(
        f"expensive_removal stats: improvements: {counter_destroy_expensive_imp}, rejected: {counter_destroy_expensive_rej}")
    print(f"route_removal stats: improvements: {counter_destroy_route_imp}, rejected: {counter_destroy_route_rej}")
    print(
        f"Weights at end of run: random_removal: {weight_destroy_random}, expensive_removal: {weight_destroy_expensive}, route_removal: {weight_destroy_route}")

    print(
        f"cheapest_insert stats: improvements: {counter_insert_cheapest_imp}, rejected: {counter_insert_cheapest_rej}")
    print(f"regret_insert stats: improvements: {counter_insert_regret_imp}, rejected: {counter_insert_regret_rej}")
    print(f"Weights at end of run: cheapest_insert: {weight_insert_cheapest}, regret_insert: {weight_insert_regret}")
    print()

    initialCost = solution_cost(initialSolution, instance, iteration)
    improvement = 100 - ((bestCost / initialCost) * 100)
    imp_per_it = improvement / (iteration + 1)
    print(f"Finished after iteration {iteration}")
    print(f"Initialization cost: {initialCost:.2f}, ourAlgorithm cost: {bestCost:.2f}.")
    print(f"We improved by {improvement:.2f}%. Average improvement per iteration: {imp_per_it:.2f}%.")
    print(f"We improved {len(listImprovingIterations)} times, in the following iterations: {listImprovingIterations}.")
    print(f"We fell back {len(listFallbackIterations)} times, in the following iterations: {listFallbackIterations}.")
    endtime = datetime.datetime.now()
    print(f"Length of the run: {endtime - starttime}.\n")
    print('accept: ' + str(accept_time) + ', iterations: ' + str(iteration) + ', ratio: ' + str(accept_time/iteration))  # todo: something seems not right here with accept_time. Seems way to high.
    print(str(endtime))




    return list(map(lambda x: x.customer_list, bestSolution))