import pandas as pd

from instances.Construction import sort_customers_by_sweep, ouralgorithm, random_sweep
from instances.LocalSearch import find_first_improvement_2Opt, find_first_improvement_relocate, \
    find_first_improvement_exchange
from instances.Route import RouteObject
from instances.Trucks import Vehicle
from instances.Utils import Instance, next_fit_heuristic_naive, compute_distances, next_fit_heuristic, is_feasible, \
    compute_total_demand, routeCost, temporaryRouteCost, compute_distance, vehicle_assignment, solution_cost
from instances.Plot import draw_routes, plotTSP

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
# df_NewYork_1_nodes = pd.read_csv("data/NewYork.1.nodes", sep=' ')
# df_NewYork_2_nodes = pd.read_csv("data/NewYork.2.nodes", sep=' ')
# df_NewYork_routes = pd.read_csv("data/NewYork.routes", sep=' ')
df_Paris_nodes = pd.read_csv("data/Paris.nodes", sep=' ')
df_Paris_routes = pd.read_csv("data/Paris.routes", sep=' ')
# df_Shanghai_nodes = pd.read_csv("data/Shanghai.nodes", sep=' ')
# df_Shanghai_routes = pd.read_csv("data/Shanghai.routes", sep=' ')

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
listOfInitialVehicles = []
dummyAtego = Vehicle("MercedesBenzAtego", "Paris", "999999") # this dummy vehicle is used after the sweep

#set all the initial conditions for vehicles here
city = "Paris"
numAtego = 10
numVWtrans = 10
numECargoBike = 5

for i in range(numAtego):
    vehicleType = "MercedesBenzAtego"
    numberplate = "1MBA" + str(i+1).zfill(3)
    listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate))
for i in range(numVWtrans):
    vehicleType = "VWTransporter"
    numberplate = "2VWT" + str(i+1).zfill(3)
    listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate))
for i in range(numECargoBike):
    vehicleType = "DouzeV2ECargoBike"
    numberplate = "7ECB" + str(i+1).zfill(3)

    listOfInitialVehicles.append(Vehicle(vehicleType, city, numberplate))

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

maxIterations = 10  # sets how many iterations we want

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
print(coordinates)

# coordinates for matplot START
# TODO: Get this shit out of main and into Plot
LonParisInt = []
LonParis = list(test_df_Paris_nodes.loc[:, "Lon"])
for lon in LonParis:
    lon = lon * 10000000
    lon = int(lon)
    LonParisInt.append(lon)

LatParisInt = []
LatParis = list(test_df_Paris_nodes.loc[:, "Lat"])
for lat in LatParis:
    lat = lat * 100000000000
    lat = int(lat)
    LatParisInt.append(lat)

coordinates_int = []
for i in range(len(LonParisInt)):
    cord_int = (LonParisInt[i], LatParisInt[i])
    coordinates_int.append(cord_int)
# coordinates for matplot END

# 4. CREATING INSTANCE
ourInstance = Instance(testDimension, listOfInitialVehicles, testDemandParis, testParisDistances, coordinates)

# 6. SWEEP HEURISTIC
""" The Sweep Heuristic will only work if we have enough payload_kg capacity to assign all customers to feasible [kg] routes"""
bestCostRandomSweep = 10e10
for i in range(10): # we run the sweep heuristic multiple times with different starting angles to get a good starting solution
    tempSolutionRandomSweep = random_sweep(ourInstance, listOfInitialVehicles)
    tempCost = solution_cost(tempSolutionRandomSweep, ourInstance, 0, True)
    # print(f"Rand Sweep Heuristic, temp distance: {compute_distances(tempSolutionRandomSweep, ourInstance)}")
    if tempCost < bestCostRandomSweep:
        solutionRandomSweep = tempSolutionRandomSweep.copy()
        bestCostRandomSweep = tempCost
print(f"Rand Sweep Heuristic, #Vehicles: {len(solutionRandomSweep)}, cost: {bestCostRandomSweep}")

plotTSP(list(map(lambda x: x.customer_list, solutionRandomSweep)), coordinates_int, 'r')  # matplot of sweep solution

# 7 CREATING ROUTE OBJECTS
initialListOfRoutes = solutionRandomSweep
# for i in solutionRandomSweep: # we turn the solution of random sweep (a nested list[list]) into a list[Route] with objects of Class Route
#     initialListOfRoutes.append(RouteObject(i, dummyAtego)) # we start all with the same truck


# 7.1 Vehicle Assignment after Sweep
# for r in initialListOfRoutes: # assigning costs to the routes, costs with the initial dummy vehicle assignment. This is needed because the vehicle assignment goes for the most expensive route first.
#     r.current_cost = routeCost(r, ourInstance, 0, False)
listOfInitAvailableVehicles = vehicle_assignment(initialListOfRoutes, listOfInitialVehicles, ourInstance, 0, True)  # vehicle_assignment(list_of_routes: list[Route], initial_list_of_vehicles: List[Vehicle], instance: Instance):

""" testing penalty costs
# initialListOfRoutes[0].customer_list.insert(1, 5)
# initialListOfRoutes[0].customer_list.insert(1, 6)
# initialListOfRoutes[0].customer_list.insert(1, 7)
# initialListOfRoutes[0].vehicle = Vehicle("DouzeV2ECargoBike", city, "000000")
test_penalty_cost = routeCost(initialListOfRoutes[0], ourInstance, 5, True)
"""

# 8. OUR ALGORITHM (DESTRUCTION + INSERTION + OPTIMIZATION + ACCEPTANCE)
solutionOur = ouralgorithm(ourInstance, initialListOfRoutes, find_first_improvement_2Opt, listOfInitialVehicles, listOfInitAvailableVehicles, maxIterations, coordinates_int)
# lenOfSolutionOur = len(solutionOur)
# for i in range(lenOfSolutionOur):
#     print(f"Sum of demands of a {i} route: " + str(compute_total_demand(solutionOur[i], ourInstance)))
# print(compute_distances(solutionOur, ourInstance))


# trying to get the matplot to work
plotTSP(solutionOur, coordinates_int, 'g')
#draw_routes(solutionOur, coordinates_int)