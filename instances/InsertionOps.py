from instances.Route import RouteObject
from instances.Trucks import Vehicle
from instances.Utils import Instance, temporaryRouteCost


def cheapest_insertion_iterative(listOfRoutes: list[RouteObject], listOfRemoved: list[int],
                                 list_of_available_vehicles: list[Vehicle], instance: Instance, iteration: int):
    while len(listOfRemoved) > 0:

        bestInsertionCost = 10e10  # very big number
        bestPosition = (0, 0)
        bestCustomer = 0


        # print(list(map(lambda x: x.current_cost, listOfRoutes)))  # printing out costs of the routes after i-th loop of the insertion phase
        for customerIndex in range(len(listOfRemoved)):  # iterating over list of removed customers
            for i in listOfRoutes:  # iterating over routes in listOfRoutes
                for j in range(len(i.customer_list) - 1):  # iterating over positions in a route
                    costWithout = i.current_cost
                    temporaryCustomerList = i.customer_list.copy()
                    temporaryCustomerList.insert(j + 1, listOfRemoved[customerIndex])
                    costWith = temporaryRouteCost(temporaryCustomerList, i.vehicle, instance, iteration, True)
                    insertionCost = costWith - costWithout
                    if (insertionCost < bestInsertionCost):  # \
                        # & (compute_total_demand(i.customer_list, instance) + instance.q[listOfRemoved[customerIndex]] < i.vehicle.payload_kg): # & feasibilityCheck(instance, listAfterDestruction, listOfRemoved, customerIndex, i)
                        bestInsertionCost = insertionCost
                        bestPosition = (i, j + 1)
                        bestCustomer = listOfRemoved[customerIndex]

        bestNewRouteCost = 10e10
        for v in list_of_available_vehicles: # check if a new route would be cheaper
            newCustomerList = [0, bestCustomer, 0]
            newRouteCost = temporaryRouteCost(newCustomerList, v, instance, iteration, True)  # check cost of new route
            if newRouteCost < bestNewRouteCost:
                bestNewRouteCost = newRouteCost
                bestNewVehicle = v

        if bestInsertionCost < bestNewRouteCost:
            bestPosition[0].customer_list.insert(bestPosition[1], bestCustomer) # insert bestCustomer to the best feasible route for them
        else:
            newRoute = RouteObject(newCustomerList, bestNewVehicle)  # create a new RouteObject
            newRoute.current_cost = newRouteCost
            listOfRoutes.append(newRoute)  # add newRoute to list of routes
            list_of_available_vehicles.remove(bestNewVehicle)

        listOfRemoved.remove(bestCustomer)  # delete current bestCustomer from a list of removed customers