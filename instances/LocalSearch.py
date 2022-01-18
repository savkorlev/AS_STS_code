####
# Procedures to improve complete solutions
from instances.Route import RouteObject
from instances.Utils import compute_distance, Solution, Instance, compute_total_demand


def hillclimbing(solution: Solution, instance: Instance, function) -> Solution:
    """
    simple improvement procedure which tries to find a (local) optima by continuously calling
    find_first_improvement_2Opt(solution, instance) until no further improvements are found.
    :param solution: list of routes to improve
    :param instance: corresponding instance
    :return: the provided solution or an improved solution
    """
    improvement = True
    while improvement: # until no improvement, 2 opt will continue
        improvement = function(solution, instance)

    return solution

def vnd(solution: Solution, instance: Instance) -> Solution:
    """
    Variable Neighborhood Decent procedure, searching three neighborhoods (2opt, relocate, exchange) in a structured
    way. Neighborhoods are ordered, if an improvement was found, the search continues from the first neighborhood.
    Otherwise the next neighborhood in order is searched. This continues until no improvements can be found.
    :param solution: list of routes to improve
    :param instance: corresponding instance
    :return: the provided solution or an improved solution
    """
    improvement = True
    while improvement:
        improvement = find_first_improvement_2Opt(solution, instance)
        if not improvement: # no improvement from 2Opt -> relocate
            improvement = find_first_improvement_relocate(solution, instance)
            # if not improvement: # no improvement from relocate -> exchange
            #     improvement = find_first_improvement_exchange(solution, instance)
    return solution

def find_first_improvement_2Opt(solution: Solution, instance: Instance) -> bool:
    """
    search for the first improving 2-opt move.
    A 2-opt consist of removing two edges and reconnecting the nodes differently but feasible way.
    In other terms, a consecutive subset of visits is reversed.
    Example: [0,1,2,3,4,5,0] => [0,1,4,3,2,5,0]
        A 2-opt could be removing edges between 1-2 and 4-5, and connecting 1-4 and 2-5.
    :param solution: list of routes to improve
    :param instance: corresponding instance
    :return: `True` if an improvement was found, otherwise `False`.
    """

    # TODO: apply improvements from the exchange neighborhood here as well

    for r_index, route in enumerate(solution): # List[Route]
        for i in range(1, len(route)-2): # i: the first position to be switched (the last index should -2)
            for j in range(i+1, len(route)-1): # j: the second position to be switched (the last index should -1)
                # [0,1,2,3,4,5,0]
                #     i^---^j
                # [0,1,4,3,2,5,0]
                # the route until (i-1) + reverse (i~j) + the route from (j+1)
                new_route = route[:i] + list(reversed(route[i:(j+1)])) + route[(j+1):]
                new_distance = compute_distance(new_route, instance)

                change = new_distance - compute_distance(route, instance)

                if change < -0.000001: # change < 0??
                    # improvement
                    solution[r_index] = new_route
                    return True
    return False

def find_first_improvement_relocate(solution: Solution, instance: Instance) -> bool:
    """
    search for the first improving relocate
    Example: [[0,1,2,0],[0,3,4,5,0]] => [[0,1,3,2,0],[0,4,5,0]]
        A relocate move could be to move customer 3 between 1 and 2.
    :param solution: list of routes to improve
    :param instance: corresponding instance
    :return: `True` if an improvement was found, otherwise `False`.
    """

    # TODO: apply improvements from the exchange neighborhood here as well

    for r1_index, r1 in enumerate(solution): # List[Route]
        for i in range(1, len(r1) - 1): # except depot, all the nodes can be relocated
            for r2_index, r2 in enumerate(solution):
                # demand of node to be relocated + total demands of route to have the relocated node > max capacity
                if instance.q[r1[i]] + compute_total_demand(r2, instance) > 2400:
                    continue

                for j in range(1, len(r2)): # relocate the node to every position of the other route
                    if r1_index == r2_index: # same route
                        # no intra route optimization
                        # TODO: implement case for intra route optimization
                        continue

                    new_r1 = r1[:i] + r1[i+1:] # node i is removed
                    new_r2 = r2[:j] + [r1[i]] + r2[j:] # [r1[i]] is the relocated node

                    change_r1 = compute_distance(new_r1, instance) - compute_distance(r1, instance)
                    change_r2 = compute_distance(new_r2, instance) - compute_distance(r2, instance)

                    if change_r1 + change_r2 < -0.000001: # if overall distance becomes smaller
                        solution[r1_index] = new_r1
                        solution[r2_index] = new_r2
                        return True
    return False

def find_first_improvement_exchange(solution: Solution, instance: Instance) -> bool:
    """
    search for the first improving exchange
    Example: [[0,1,2,0],[0,3,4,5,0]] => [[0,4,2,0],[0,3,1,5,0]]
        A exchange move could be to swap customer 4 between 1.
    :param solution: list of routes to improve
    :param instance: corresponding instance
    :return: `True` if an improvement was found, otherwise `False`.
    """

    current_distances = []
    for route in solution:
        current_distances.append(compute_distance(route, instance))

    current_demand = []
    for route in solution:
        current_demand.append(compute_total_demand(route, instance))

    for r1_index, r1 in enumerate(solution):
        for i in range(1, len(r1)-1): # except depot, all the nodes can be relocated

            # TODO: remove symmetry in the neighborhood - each pair exchange is tested twice!

            for r2_index, r2 in enumerate(solution):
                if r1_index == r2_index: # same route
                    # no intra route optimization for now
                    # TODO: implement case for intra route optimization
                    continue

                for j in range(1, len(r2) - 1):
                    # demand of route 1 - demand of swapped node in route 1 + demand of swapped node in route 2
                    new_demand_r1 = current_demand[r1_index] - instance.q[r1[i]] + instance.q[r2[j]]
                    # demand of route 2 - demand of swapped node in route 2 + demand of swapped node in route 1
                    new_demand_r2 = current_demand[r2_index] - instance.q[r2[j]] + instance.q[r1[i]]

                    if new_demand_r1 > 2400 or new_demand_r2 > 2400: # exceed max capacity
                        continue
                    # - dist(i-1, i) - dist(i, i+1) + dist(i-1, j) + dist(j, i+1)
                    change_r1 = - instance.d[r1[i - 1], r1[i]] \
                                - instance.d[r1[i], r1[i+1]] \
                                + instance.d[r1[i-1], r2[j]] \
                                + instance.d[r2[j], r1[i+1]]
                    # - dist(j-1, j) - dist(j, j+1) + dist(j-1, i) + dist(i, j+1)
                    change_r2 = - instance.d[r2[j - 1], r2[j]] \
                                - instance.d[r2[j], r2[j + 1]] \
                                + instance.d[r2[j - 1], r1[i]] \
                                + instance.d[r1[i], r2[j + 1]]

                    if change_r1 + change_r2 < -0.000001: # if overall distance becomes smaller
                        # only create the new route if it's an improvement
                        new_r1 = r1[:i] + [r2[j]] + r1[i + 1:]
                        new_r2 = r2[:j] + [r1[i]] + r2[j + 1:]

                        solution[r1_index] = new_r1
                        solution[r2_index] = new_r2
                        return True
    return False

def find_best_improvement_2Opt(solution: Solution, instance: Instance) -> bool:
    """
    search for the best improving 2-opt move.

    :param solution: list of routes to improve
    :param instance: corresponding instance
    :return: `True` if an improvement was found, otherwise `False`.
    """
    # https://github.com/saper0/tsp-heuristics/blob/master/ls_2opt.py

    for r_index, route in enumerate(solution): # List[Route]
        best_2opt = None
        best_distance = compute_distance(route, instance)
        for i in range(1, len(route)-2): # i: the first position to be switched (the last index should -2)
            for j in range(i+1, len(route)-1): # j: the second position to be switched (the last index should -1)
                new_route = route[:i] + list(reversed(route[i:(j+1)])) + route[(j+1):]
                new_distance = compute_distance(new_route, instance)

                change = new_distance - best_distance

                if change < -0.000001:
                    # improvement
                    best_distance = new_distance
                    best_2opt = (i, j)
        if best_2opt is not None:
            solution[r_index] = route[:best_2opt[0]] + list(reversed(route[best_2opt[0]:(best_2opt[1]+1)])) + route[(best_2opt[1]+1):]
            return True
    return False


def find_first_improvement_exchange_christopher(list_of_Routes: list[RouteObject], instance: Instance) -> bool:
    """
    search for the first improving exchange
    Example: [[0,1,2,0],[0,3,4,5,0]] => [[0,4,2,0],[0,3,1,5,0]]
        A exchange move could be to swap customer 4 between 1.
    :param list_of_Routes: list of routes to improve
    :param instance: corresponding instance
    :return: `True` if an improvement was found, otherwise `False`.
    """

    current_distances = []
    for route in solution:
        current_distances.append(compute_distance(route, instance))

    current_demand = []
    for route in solution:
        current_demand.append(compute_total_demand(route, instance))

    for r1_index, r1 in enumerate(solution):
        for i in range(1, len(r1)-1): # except depot, all the nodes can be relocated

            # TODO: remove symmetry in the neighborhood - each pair exchange is tested twice!

            for r2_index, r2 in enumerate(solution):
                if r1_index == r2_index: # same route
                    # no intra route optimization for now
                    # TODO: implement case for intra route optimization
                    continue

                for j in range(1, len(r2) - 1):
                    # demand of route 1 - demand of swapped node in route 1 + demand of swapped node in route 2
                    new_demand_r1 = current_demand[r1_index] - instance.q[r1[i]] + instance.q[r2[j]]
                    # demand of route 2 - demand of swapped node in route 2 + demand of swapped node in route 1
                    new_demand_r2 = current_demand[r2_index] - instance.q[r2[j]] + instance.q[r1[i]]

                    if new_demand_r1 > 2400 or new_demand_r2 > 2400: # exceed max capacity
                        continue
                    # - dist(i-1, i) - dist(i, i+1) + dist(i-1, j) + dist(j, i+1)
                    change_r1 = - instance.d[r1[i - 1], r1[i]] \
                                - instance.d[r1[i], r1[i+1]] \
                                + instance.d[r1[i-1], r2[j]] \
                                + instance.d[r2[j], r1[i+1]]
                    # - dist(j-1, j) - dist(j, j+1) + dist(j-1, i) + dist(i, j+1)
                    change_r2 = - instance.d[r2[j - 1], r2[j]] \
                                - instance.d[r2[j], r2[j + 1]] \
                                + instance.d[r2[j - 1], r1[i]] \
                                + instance.d[r1[i], r2[j + 1]]

                    if change_r1 + change_r2 < -0.000001: # if overall distance becomes smaller
                        # only create the new route if it's an improvement
                        new_r1 = r1[:i] + [r2[j]] + r1[i + 1:]
                        new_r2 = r2[:j] + [r1[i]] + r2[j + 1:]

                        solution[r1_index] = new_r1
                        solution[r2_index] = new_r2
                        return True
    return False