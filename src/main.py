import sys

import pandas as pd

from instances.Construction import ouralgorithm
from instances.Intialization import random_sweep
from instances.Trucks import create_vehicles
from instances.Utils import Instance, vehicle_assignment, solution_cost
from instances.Plot import plotTSP, create_list_int_coordinates

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

# 2. CREATING TEST DATASET AND ATTRIBUTES OF FUTURE INSTANCE
#set testDimension to 1 more than customers
testDimension = 1 + 112  # change this to use more or less customers of the data set. Max for Paris is 112. Also need to change the iloc for the nodes file

# DON'T FORGET TO SET MORE VEHICLES IF YOU HAVE MORE CUSTOMERS

if testDimension == 20:
    test_df_Paris_nodes = df_Paris_nodes.iloc[:20, :]                   # select elements from D0 to C19 in nodes
    test_df_Paris_routes = df_Paris_routes.iloc[:2260, :]               # select elements from D0 to C19 in routes
if testDimension == 40:
    test_df_Paris_nodes = df_Paris_nodes.iloc[:40, :]                   # select elements from D0 to C40 in nodes
    test_df_Paris_routes = df_Paris_routes.iloc[:4633, :]               # select elements from D0 to C40 in routes
if testDimension == 113:
    test_df_Paris_nodes = df_Paris_nodes                                  # select all elements (choose if 112 customers)
    test_df_Paris_routes = df_Paris_routes                                # select all elements (choose if 112 customers)
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
print(coordinates)

# coordinates for matplot
coordinates_int = create_list_int_coordinates(test_df_Paris_nodes)

# 3. CREATING OUR VEHICLES
# set the # of vehicles available to Sweep and Algorithm
city = "Paris"
num_Atego = 19
num_VWTrans = 0
num_eCargoBike = 0
# TODO: Since we dont have to deal with multiple trips, we can change a lot of checks that test routeCost for every available vehicle. They will check the same vehicle type multiple times. We only have to check once per vehicle type + check if at least 1 is available. Check regret_insert for how this can be done.

# create vehicles via function in Trucks.py-file
listOfInitialVehicles = create_vehicles(city, num_Atego, num_VWTrans, 0, 0, 0, 0, num_eCargoBike)
print(f"List of initial Vehicle payloads_kg: {list(map(lambda x: x.payload_kg, listOfInitialVehicles))}")

# test feasibility of our vehicle assignment. Need enough capacity to carry all demand.
sumOfDemand = sum(testDemandParis)
sumOfCapacity = num_Atego * 2800 + num_VWTrans * 883 + num_eCargoBike * 100
if sumOfCapacity < sumOfDemand:
    print(f"Not enough Capacity ({sumOfCapacity}) for Demand ({sumOfDemand})")
#     # sys.exit()

# 4. SET MAX ITERATIONS
""" logically, this should not be here. But this way we have all the parameters we need to set for a run nearby"""
maxIterations = 500  # sets how many iterations we want

# 5. CREATING INSTANCE
ourInstance = Instance(testDimension, listOfInitialVehicles, testDemandParis, testParisDistances, coordinates)

# testing new sweep heuristic



# 6. SWEEP HEURISTIC
""" The Sweep Heuristic will only work if we have enough payload_kg capacity to assign all customers to feasible [kg] routes"""
bestCostRandomSweep = 10e10
for i in range(10): # we run the sweep heuristic multiple times with different starting angles to get a good starting solution
    tempSolutionRandomSweep = random_sweep(ourInstance, listOfInitialVehicles)
    tempCost = solution_cost(tempSolutionRandomSweep, ourInstance, 0, True)
    # print(f"Rand Sweep Heuristic, temp distance: {compute_distances(tempSolutionRandomSweep, ourInstance)}")
    if tempCost < bestCostRandomSweep:
        bestSolutionRandomSweep = tempSolutionRandomSweep.copy()
        bestCostRandomSweep = tempCost
print(f"Rand Sweep Heuristic, #Vehicles: {len(bestSolutionRandomSweep)}, cost: {bestCostRandomSweep}")

# plotTSP(list(map(lambda x: x.customer_list, bestSolutionRandomSweep)), coordinates_int, 'r')  # matplot of sweep solution

# 6.1 VehicleSwap for the SweepSolution
listOfInitAvailableVehicles = vehicle_assignment(bestSolutionRandomSweep, listOfInitialVehicles, ourInstance, 0, True)  # vehicle_assignment(list_of_routes: list[Route], initial_list_of_vehicles: List[Vehicle], instance: Instance):


# 7. OUR ALGORITHM (DESTRUCTION + INSERTION + OPTIMIZATION + ACCEPTANCE)
solutionOur = ouralgorithm(ourInstance, bestSolutionRandomSweep, listOfInitialVehicles, listOfInitAvailableVehicles, maxIterations, coordinates_int)
# lenOfSolutionOur = len(solutionOur)
# for i in range(lenOfSolutionOur):
#     print(f"Sum of demands of a {i} route: " + str(compute_total_demand(solutionOur[i], ourInstance)))
# print(compute_distances(solutionOur, ourInstance))
plotTSP(solutionOur, coordinates_int, 'g')
plotTSP(solutionOur, coordinates_int, 'g', False)
