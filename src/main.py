import pandas as pd

from instances.Construction import sort_customers_by_sweep, ouralgorithm, random_sweep
from instances.LocalSearch import find_first_improvement_2Opt, find_first_improvement_relocate, \
    find_first_improvement_exchange
from instances.Route import RouteObject
from instances.Trucks import Vehicle
from instances.Utils import Instance, next_fit_heuristic_naive, compute_distances, next_fit_heuristic, is_feasible, \
    compute_total_demand, routeCost, temporaryRouteCost, compute_distance

# import os
# os.chdir('C:/Users/Евгений/Desktop/TUM/WS 2021-2022/Advanced Seminar Sustainable Transportation Systems/AS_STS_code')
# os.chdir('C:/Users/Maximilian Sammer/PycharmProjects/AS_STS_code/')
# os.chdir('/Users/tuminyu/Desktop/Cory/TUM Master/Advanced Seminar/Code/Project')
# os.chdir('C:/Users/Christopher/PycharmProjects/AS_STS_code/')

### may come in handy later on:
# from src import TSPLibReader
# instance = TSPLibReader.read("instances/carModel1.vrp") //using .vrp
###

# 1. LOADING THE DATA
df_NewYork_1_nodes = pd.read_csv("data/NewYork.1.nodes", sep=' ')
df_NewYork_2_nodes = pd.read_csv("data/NewYork.2.nodes", sep=' ')
df_NewYork_routes = pd.read_csv("data/NewYork.routes", sep=' ')
df_Paris_nodes = pd.read_csv("data/Paris.nodes", sep=' ')
df_Paris_routes = pd.read_csv("data/Paris.routes", sep=' ')
df_Shanghai_nodes = pd.read_csv("data/Shanghai.nodes", sep=' ')
df_Shanghai_routes = pd.read_csv("data/Shanghai.routes", sep=' ')

# # .loc[] - access the data by the name
# print(df_NewYork_1_nodes.loc[:, "Duration"])  #select all rows and the "Duration" column
# print(type(df_NewYork_1_nodes.loc[:, "Duration"]))  #return type - Series
#
# print(df_NewYork_1_nodes.loc[:, ["Duration"]])  #select all rows and the "Duration" column
# print(type(df_NewYork_1_nodes.loc[:, ["Duration"]]))  #return type - DataFrame
#
# # .iloc[] - access the data by its number
# print(df_NewYork_1_nodes.iloc[:, 2])  #select all rows and the third column
# print(df_NewYork_1_nodes.iloc[2, 2])  #select the third row and the third column

# 2. CREATING OUR TRUCKS
truck1 = Vehicle("MercedesBenzAtego", "Paris", "000000")
truck2 = Vehicle("VWTransporter", "Paris", "000001")
truck3 = Vehicle("DouzeV2ECargoBike", "Paris", "000002")
listOfInitialVehicles = [truck1, truck2, truck3] # this needs to be filled with the vehicles the company has availiable
listOfAvailableVehicles = listOfInitialVehicles.copy()

print(f"List of initial Vehicle payloads_kg: {list(map(lambda x: x.payload_kg, listOfInitialVehicles))}")  # MAP THINGY

# 3. CREATING TEST DATASET AND ATTRIBUTES OF FUTURE INSTANCE
testDimension = 40  # change this to use more or less customers of the data set. Max for Paris is 112. Also need to change the iloc for the nodes file

# test_df_Paris_nodes = df_Paris_nodes.iloc[:20, :]                   # select elements from D0 to C19 in nodes
# test_df_Paris_routes = df_Paris_routes.iloc[:2260, :]               # select elements from D0 to C19 in routes
test_df_Paris_nodes = df_Paris_nodes.iloc[:40, :]                   # select elements from D0 to C40 in nodes
test_df_Paris_routes = df_Paris_routes.iloc[:4633, :]               # select elements from D0 to C40 in routes
# test_df_Paris_nodes = df_Paris_nodes
# test_df_Paris_routes = df_Paris_routes
# print(test_df_Paris_nodes)
# print(test_df_Paris_routes)

testDemandParis = list(test_df_Paris_nodes.loc[:, "Demand[kg]"])    # select demand column and convert it to a list
# print(testDemandParis)

testParisDistances = {}                                             # the purpose of the following up loop is
for row, content in test_df_Paris_routes.iterrows():                # to create tuples with distances from one Id
    key = (int(content[0][1:]), int(content[1][1:]))                # to another
    testParisDistances[key] = content[2]
# print(testParisDistances)

coordinates = []
for row, content in test_df_Paris_nodes.iterrows():
    coordinate = (content[1], content[2])
    coordinates.append(coordinate)

# 4. CREATING INSTANCE
ourInstance = Instance(testDimension, listOfInitialVehicles, testDemandParis, testParisDistances, coordinates)
print(coordinates)

# 5. SIMPLE SOLUTION
# solution = next_fit_heuristic_naive(ourInstance)
# print(f"Next-Fit-Heuristic | #Vehicles: {len(solution)}, distance: {compute_distances(solution, ourInstance)}")

# 6. SWEEP HEURISTIC
# solutionSweep = next_fit_heuristic(sort_customers_by_sweep(ourInstance), ourInstance)
# print(f"Sweep Heuristic | #Vehicles: {len(solutionSweep)}, distance: {compute_distances(solutionSweep, ourInstance)}, is_feasible: {is_feasible(solutionSweep, ourInstance)}")
bestDistanceRandomSweep = 10e10
for i in range(10): # we run the sweep heuristic multiple times with different starting angles to get a good starting solution
    tempSolutionRandomSweep = random_sweep(ourInstance)
    tempDistance = compute_distances(tempSolutionRandomSweep, ourInstance)
    # print(f"Rand Sweep Heuristic, temp distance: {compute_distances(tempSolutionRandomSweep, ourInstance)}")
    if  tempDistance < bestDistanceRandomSweep:
        solutionRandomSweep = tempSolutionRandomSweep.copy()
        bestDistanceRandomSweep = tempDistance
print(f"Rand Sweep Heuristic, #Vehicles: {len(solutionRandomSweep)}, distance: {compute_distances(solutionRandomSweep, ourInstance)}")

# 7 CREATING ROUTE OBJECTS
initialListOfRoutes = []
for i in solutionRandomSweep: # we turn the solution of random sweep (a nested list[list]) into a list[Route] with objects of Class Route
    initialListOfRoutes.append(RouteObject(i, truck1)) # we start all with the same truck
"""
trying to build the vehicle assignment phase
doesnt work yet, because we have no penalty costs
"""
for r in initialListOfRoutes: # assigning costs to the routes, costs with the initial vehicle assignment
    r.current_cost = routeCost(r, ourInstance)

initialListOfRoutes.sort(key=lambda x: x.current_cost, reverse=True) # orders routes by cost descending
print(f"Routes costs descending: {list(map(lambda x: x.current_cost, initialListOfRoutes))}")

for r in initialListOfRoutes: # check all routes. Before this they should be ordered by their costs descending
    # costBefore = r.current_cost
    bestVehicle = truck1
    bestCost = 10e10
    for v in listOfAvailableVehicles:  # check all available vehicles. This list should get shorter while we progress, because the best vehicles will be removed from it
        if compute_total_demand(r.customer_list, ourInstance) < v.payload_kg:
            tempCost = temporaryRouteCost(r.customer_list, v, ourInstance) # cost with the checked vehicle
            if tempCost < bestCost:  # needs a feasibility check until we get penalty costs
                bestVehicle = v
                bestCost = tempCost
    r.vehicle = bestVehicle  # assign the bestVehicle to the route
    listOfAvailableVehicles.remove(bestVehicle)  # remove the bestVehicle from available.
    r.current_cost = routeCost(r, ourInstance)  # update the route cost
    print(f"Route cost after Vehicle Assignment: route {r}, vehicle {r.vehicle.type} {r.vehicle.plateNr}, cost: {r.current_cost}")






# for r in initialListOfRoutes:


# print(initialListOfRoutes)


# 7. OUR ALGORITHM (DESTRUCTION + INSERTION + OPTIMIZATION + ACCEPTANCE)
solutionOur = ouralgorithm(ourInstance, initialListOfRoutes, find_first_improvement_2Opt)
lenOfSolutionOur = len(solutionOur)
for i in range(lenOfSolutionOur):
    print(f"Sum of demands of a {i} route: " + str(compute_total_demand(solutionOur[i], ourInstance)))
print(compute_distances(solutionOur, ourInstance))
#
# # 8. TRUCK ASSIGNING
# assignedTrucksOurAlgorithm = truckAssigning(solutionOur, ourInstance)
# print(assignedTrucksOurAlgorithm[0])
# print(assignedTrucksOurAlgorithm[1])
# print(assignedTrucksOurAlgorithm[2])
# print(assignedTrucksOurAlgorithm[3])
