from instances.Route import RouteObject
from instances.Trucks import Vehicle
from instances.Utils import Instance, temporaryRouteCost, routeCost


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


def regret_insertion(listOfRoutes: list[RouteObject], listOfRemoved: list[int],
                     list_of_available_vehicles: list[Vehicle], instance: Instance, iteration: int):
    while len(listOfRemoved) > 0:  # TODO: the last customer could go to his best position immediately. This can be problematic if only 1 customer was removed at the start.
        regret_tupleList = []  # will hold all customers and their regrets + best position

        # print(list(map(lambda x: x.current_cost, listOfRoutes)))  # printing out costs of the routes after i-th loop of the insertion phase
        for customerIndex in range(len(listOfRemoved)):  # iterating over list of removed customers
            current_customer = listOfRemoved[customerIndex]
            customer_cost_tupleList = []

            bestNewRouteCost = 10e10
            lastVehicleType = "noVehicle"
            for v in list_of_available_vehicles:  # check the cost of the cheapest new route with our customer
                if v.type != lastVehicleType:
                    newCustomerList = [0, current_customer, 0]
                    newRouteCost = temporaryRouteCost(newCustomerList, v, instance, iteration, True)  # check cost of new route
                    if newRouteCost < bestNewRouteCost:
                        bestNewRouteCost = newRouteCost
                        bestNewVehicle = v
                lastVehicleType = v.type
            customer_cost_tupleList.append((bestNewRouteCost, "new_route", v))

            for i in listOfRoutes:  # iterating over routes in listOfRoutes
                for j in range(len(i.customer_list) - 1):  # iterating over positions in a route
                    costWithout = i.current_cost
                    temporaryCustomerList = i.customer_list.copy()
                    temporaryCustomerList.insert(j + 1, current_customer)  # j + 1 since we start after the depot
                    costWith = temporaryRouteCost(temporaryCustomerList, i.vehicle, instance, iteration, True)
                    insertionCost = costWith - costWithout

                    customer_cost_tupleList.append((insertionCost, i, j))  # filling a tupleList with insertionCost & position

            customer_cost_tupleList.sort(key=lambda y: y[0], reverse=False)  # sort the list by cost, ascending.
            customerRegret = customer_cost_tupleList[1][0] - customer_cost_tupleList[0][0]  # 2nd cheapest cost - cheapest cost = regret
            customerBestRote = customer_cost_tupleList[0][1]
            customerBestPosition = customer_cost_tupleList[0][2]
            # add all needed information to a list which will hold all customers, their regret and their position
            regret_tupleList.append((current_customer, customerRegret, customerBestRote, customerBestPosition))

        regret_tupleList.sort(key=lambda y: y[1], reverse=True)  # sort the customers descending by their regret
        best_customer = regret_tupleList[0][0]
        best_route = regret_tupleList[0][2]
        best_position = regret_tupleList[0][3]

        if best_route == "new_route":
            best_vehicle = regret_tupleList[0][3]
            newRoute = RouteObject([0, best_customer, 0], best_vehicle)  # create a new RouteObject
            newRoute.current_cost = routeCost(newRoute, instance, iteration, True)
            listOfRoutes.append(newRoute)  # add newRoute to list of routes
            list_of_available_vehicles.remove(bestNewVehicle)
        else:
            best_route.customer_list.insert(best_position + 1, best_customer)

        listOfRemoved.remove(best_customer)  # delete current bestCustomer from a list of removed customers