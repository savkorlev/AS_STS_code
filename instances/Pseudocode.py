"""
I will use this file to write pseudocode whenever I dont know exactly how to code something
- Christopher 2022.01.06
"""

from instances.Utils import routeCost
import math
import random
from typing import List


# Pseudocode for Class Route
class Route:
    list customer_list = [0,0] # the list of customers (+depots)
    Vehicle vehicle = "" # each route should know the vehicle object assigned to it. not just the vehicle type, but the vehicles unique ID / numberplate
    boolean currently_feasible = false # each route should know if it is currently feasible. Everytime the route_cost is updated, we should also be told if the route is feasible (penalty_cost = 0)
    int current_cost = 0 # whenever we update the route_cost, we should store it in the route. We will often compare against the cost of the unchanged route (e.g. for insert-operations), so it makes sense to have it stored

def CreateRoute(initialCustomer, vehicle, instance) -> Route
    newRoute = new Route
    newRoute.customer_list = [0, initialCustomer, 0]
    newRoute.vehicle = vehicle
    newRoute.currently_feasible = false
    newRoute.current_cost = routeCost(vehicle, newRoute, instance)

    return newRoute

# Pseudocode for Class Vehicle
"""
I believe it would be best if all vehicles are the same class, and are specialized by their parameters.

I also thing it would be best if we handle the cities+vehicle-type influence on the object in a function CreateVehicle(city, vehicle_type, numberplateParent)
This function would know the city and the vehicle type and then set all the parameters of the created object accordingly
It should also be able to create dummy vehicles (with e.g. 5h remaining) by knowing the parent vehicles numberplateParent

"""
class Vehicle:
    string vehicle_id # the vehicle id is probably needed to attach the vehicle to a route
    string vehicle_type # vehicle type is needed to set constraints & prices
    string vehicle_numberplate # numberplate is my way to connect Vehicles and their Dummy-Vehicles. We will need to get penalty costs over all vehicles with the same numberplate, so they need to know it
    boolean is_electric # could be used to differentiate between ICEV & BEV. This is important because ICEVs will also need to pass their batterie charge (range) to their dummies. ICEVs can be refuelled.

    int cost_per_km_inside
    int cost_per_km_outside
    int cost_per_min
    int fixed_cost # fixed costs are used for the uncapped runs which tell us the best fleet mix. In capped runs, they are 0

    int payload_kg
    int payload_vol
    int range # we can use range for both ICEV & BEV
    int operating_hours



# Pseudocode for VehicleSwapOperation
def VehicleSwapOperation(list_of_routes, list_of_initial_vehicles):  # ListOfInitialVehicles should probably be global. It also never gets changed.
    sorted_routes = sorted(list_of_routes, 'sort by route_cost in descending order')  # sort the routes by their cost, so we can start with the most expensive route. More expensive routes have more potential to get savings by getting the best vehicle
    # it seems like it would generally be smart if a route knew its current cost, so we dont have to constantly recalculate it

    list_of_available_vehicles = list_of_initial_vehicles  # we reset all vehicles to initial

    while len(sorted_routes) > 0:  # for every route we need to find he cheapest vehicle type
        cheapest_route_cost = 10e10  # to track which vehicle assignment gives the cheapest route
        for av in list_of_available_vehicles:
            temp_route_cost = routeCost(sorted_routes[0], list_of_available_vehicles[
                av])  # get the route_cost (transport_cost + penalty cost) for each vehicle type. Start with the most expensive route
            if temp_route_cost < cheapest_route_cost:
                cheapest_route_cost = temp_route_cost  # update cheapest route cost
                bestVehicle = av  # update cheapest vehicle

        sorted_routes[0].vehicle = list_of_available_vehicles[bestVehicle]  # assign the cheapest vehicle to the route
        sorted_routes.remove(
            0)  # remove the most expensive route from the sorted list of routes, so we can continue with the next route

        newVehicle = CreateDummyVehicle(list_of_available_vehicles[bestVehicle])  # creates a dummy vehicle from the remaining resources (time&batteries) of the best vehicle. This function needs to be written.
        list_of_available_vehicles.append(newVehicle)  # Add the dummy vehicle to the list of available vehicles
        list_of_available_vehicles.remove(bestVehicle)  # remove the bestVehicle from the list of available vehicles

        # if we never assign an initial vehicle to a route, no dummy vehicle of this vehicle is created


# pseudocode for cheapestRemoval()
def Removal(solution, 'randomRemovalWeight, expensiveRemovalWeight') -> solution, 'string':
    numberOfRemoved = random.randint(round(0.1 * (len(instance.q) - 1)), round(0.5 * (len(instance.q) - 1)))  # generate number customers to be removed

    rand = random.randint(0,1) #this will be the adaptive part. Instead of doing 90% / 10%, do smart adaptive stuff.
    if rand > 0.1:
        randomRemoval(solution, numberOfRemoved)
        # removalOperation = randomRemoval
    else:
        expensiveRemoval(solution, numberOfRemoved)
        # removalOperation = expensiveRemoval

    listAfterDestruction = []
    for i in range(len(solution)):
        element = [e for e in solution[i] if e not in listOfRemoved]
        listAfterDestruction.append(element)
    print(f"Customers to be removed: {listOfRemoved}")
    print(f"Routes after destruction: {listAfterDestruction}")
    return listAfterDestruction
    # return removalOperation # in order to know how to change the adaptive weights, we need to know which operation was chosen

def randomRemoval(solution, numberOfRemoved) -> list:
    listOfRemoved = random.sample(range(1, len(instance.q)), numberOfRemoved)  # generate customers to be removed, starting from 1 so depo isn't getting deleted
    return listOfRemoved

def expensiveRemoval(solution, numberOfRemoved) -> list:
    list_of_customer_cost = []
    for 'every route in the solution':
        rC = routeCost(route) # get cost of the route with all customers
        for 'every customer in the route': # not the depot
            temp_route = route.remove(customer) # remove the current customer from the route
            crC = routeCost(temp_route) # get the cost with customer removed
            cC = rC - crC # get the cost of the customer
            list_of_customer_cost.append(cC)

    listOfRemoved = # get the numberOfRemoved highest costs from the list_of_customer_cost
    return listOfRemoved