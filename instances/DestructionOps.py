import random

from instances.Route import RouteObject
from instances.Utils import Instance, temporaryRouteCost, routeCost


def random_removal(instance: Instance) -> list:
    """ random removal simply samples from the customer list in instance.q
    """
    numberOfRemoved = random.randint(round(0.05 * (len(instance.q) - 1)), round(0.15 * (len(instance.q) - 1)))  # generate number customers to be removed
    listOfRemoved = random.sample(range(1, len(instance.q)),
                                  numberOfRemoved)  # generate customers to be removed, starting from 1 so depo isn't getting deleted
    return listOfRemoved

def route_removal(list_of_routes: list[RouteObject]) -> list:
    listOfRemoved = []
    sacrifice_route = random.choice(list_of_routes)
    numberOfRemoved = random.randint(round(0.5 * (len(sacrifice_route.customer_list) - 2)),
                                     round(1 * (len(sacrifice_route.customer_list) - 2)))  # generate number customers to be removed

    for i in range(numberOfRemoved):
        listOfRemoved.append(sacrifice_route.customer_list[i+1])  # add customers to the list

    return listOfRemoved


def expensive_removal(currentSolution: list[RouteObject], instance: Instance, iteration: int) -> list:
    """
    checks the cost of every single customer by comparing the cost of the route with this customer vs the cost of the
    route without the customer.
    :param currentSolution: list of RouteObjects
    :param instance:
    :param iteration: needed because penalty costs in routeCosts depend on iteration
    :return:
    """
    for r in currentSolution:
        r.current_cost = routeCost(r, instance, iteration, True) # recalculate all the routeCosts. Because we start a new iteration, penalty costs are updated.

    numberOfRemoved = random.randint(round(0.1 * (len(instance.q) - 1)), round(0.1 * (len(instance.q) - 1)))  # generate number customers to be removed
    tupleList = []  # we will save all customers and their cost in this list, so we can later sort by cost
    for r in currentSolution:  # iterate over all routes
        complete_route = r.customer_list.copy()  # make a copy so we dont accidentally change the route inside the routeObject
        for customer in complete_route:  # check all the customers
            if customer != 0:  # dont remove depots
                temp_route = complete_route.copy()
                temp_route.remove(customer)  # create a temp route without our customer
                # compare the costs of the route vs route without customer.
                customer_cost = r.current_cost - temporaryRouteCost(temp_route, r.vehicle, instance, iteration, True)
                tupleList.append((customer, customer_cost))  # add the customer and his cost to our tupleList

    tupleList.sort(key=lambda y: y[1], reverse=True)  # sort the tuple list by customer_cost
    listOfRemoved = []
    for i in range(0, numberOfRemoved):  # get the n=numberOfRemoved most expensive customers
        listOfRemoved.append(tupleList[i][0])  # add them to our return-list

    return listOfRemoved