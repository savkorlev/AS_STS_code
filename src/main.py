import sys
import copy
import time

import pandas as pd

from instances.Construction import ouralgorithm
from instances.Intialization import random_sweep
from instances.Trucks import create_vehicles
from instances.Utils import Instance, vehicle_assignment, solution_cost, find_cheapest_vehicle
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
df_Paris_nodes["Duration"] = pd.to_timedelta(df_Paris_nodes["Duration"]).dt.total_seconds() / 60  # converting duration column to floats instead of strings
df_Paris_routes = pd.read_csv("data/Paris.routes", sep=' ')
df_Paris_routes["Duration[s]"] = pd.to_timedelta(df_Paris_routes["Duration[s]"]).dt.total_seconds() / 60  # converting duration column to floats instead of strings
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
# 1 + either 19, 39 or 112

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

testDemandParis = list(test_df_Paris_nodes.loc[:, "Demand[kg]"])    # select demand column (in kg) and convert it to a list
# print(testDemandParis)
testDemandParisVolume = list(test_df_Paris_nodes.loc[:, "Demand[m^3*10^-3]"])    # select demand column (in volume) and convert it to a list
# print(testDemandParisVolume)
testParisCustomerDuration = list(test_df_Paris_nodes.loc[:, "Duration"])  # select duration column (in volume) and convert it to a list
# print(testParisCustomerDuration)

testParisDistances = {}                                             # the purpose of the following up loop is
for row, content in test_df_Paris_routes.iterrows():                # to create tuples with distances from one Id
    key = (int(content[0][1:]), int(content[1][1:]))                # to another
    testParisDistances[key] = content[2]
# print(testParisDistances)

testParisDistancesInside = {}                                       # the purpose of the following up loop is
for row, content in test_df_Paris_routes.iterrows():                # to create tuples with distances from one Id
    key = (int(content[0][1:]), int(content[1][1:]))                # to another inside the city
    testParisDistancesInside[key] = content[3]
# print(testParisDistancesInside)

testParisDistancesOutside = {}                                      # the purpose of the following up loop is
for row, content in test_df_Paris_routes.iterrows():                # to create tuples with distances from one Id
    key = (int(content[0][1:]), int(content[1][1:]))                # to another outside the city
    testParisDistancesOutside[key] = content[4]
# print(testParisDistancesOutside)

testParisArcDuration = {}                                           # the purpose of the following up loop is
for row, content in test_df_Paris_routes.iterrows():                # to create tuples with durations from one Id
    key = (int(content[0][1:]), int(content[1][1:]))                # to another inside the city
    testParisArcDuration[key] = content[5]
# print(testParisArcDuration)

coordinates = []
for row, content in test_df_Paris_nodes.iterrows():
    coordinate = (content[1], content[2])
    coordinates.append(coordinate)
# print(coordinates)

# coordinates for matplot
coordinates_int = create_list_int_coordinates(test_df_Paris_nodes)

# 3. CREATING OUR VEHICLES
# set the # of vehicles available to Sweep and Algorithm
city = "Paris"
numI_Atego = 20
numI_VWTrans = 50
numI_VWCaddy = 50
numI_DeFuso = 20
numI_ScooterL = 50
numI_ScooterS = 50
numI_eCargoBike = 0

# create vehicles via function in Trucks.py-file
listOfInitialVehicles = create_vehicles(city, numI_Atego, numI_VWTrans, numI_VWCaddy, numI_DeFuso, numI_ScooterL, numI_ScooterS, numI_eCargoBike)
print(f"List of initial Vehicle payloads_kg: {list(map(lambda x: x.payload_kg, listOfInitialVehicles))}")

# test feasibility of our vehicle assignment. Need enough capacity to carry all demand.
sumOfDemand = sum(testDemandParis)
sumOfCapacity = numI_Atego * 2800 + numI_VWTrans * 883 + numI_VWCaddy * 670 + numI_DeFuso * 2800 + numI_ScooterL * 905 + numI_ScooterS * 720 + numI_eCargoBike * 100
if sumOfCapacity < sumOfDemand:
    print(f"Not enough Capacity ({sumOfCapacity}) for Demand ({sumOfDemand})")
    sys.exit()

# # 5. SET MAX ITERATIONS
# """ logically, this should not be here. But this way we have all the parameters we need to set for a run nearby"""
# maxIterations = 3000  # sets how many iterations we want
# maxTime = 18.0  # in Seconds. Sets how much time the loop should maximally use
# ITERATION PARAMETERS ARE NOW SET IN THE INSTANCE

# 5. CREATING INSTANCE
ourInstance = Instance(testDimension, listOfInitialVehicles, testDemandParis, testDemandParisVolume, testParisCustomerDuration,
                       testParisDistances, testParisDistancesInside, testParisDistancesOutside, testParisArcDuration, coordinates)

# # SET PARAMETERS of SIMULATED ANNEALING
# init_temp = 0.9
# cooling = 0.85
# SIM ANNEALING PARAMETERS ARE NOW SET IN THE INSTANCE


# 6. SWEEP HEURISTIC
""" The Sweep Heuristic will only work if we have enough payload_kg capacity to assign all customers to feasible [kg] routes"""
bestCostRandomSweep = 10e10
for i in range(10): # we run the sweep heuristic multiple times with different starting angles to get a good starting solution
    tempSolutionRandomSweep = random_sweep(ourInstance, listOfInitialVehicles)
    tempCost = solution_cost(tempSolutionRandomSweep, ourInstance, 0, True)
    # print(f"Rand Sweep Heuristic, temp distance: {compute_distances(tempSolutionRandomSweep, ourInstance)}")
    if tempCost < bestCostRandomSweep:
        bestSolutionRandomSweep = copy.deepcopy(tempSolutionRandomSweep)
        bestCostRandomSweep = tempCost
print(f"Rand Sweep Heuristic, #Vehicles: {len(bestSolutionRandomSweep)}, cost: {bestCostRandomSweep}")

# plotTSP(list(map(lambda x: x.customer_list, bestSolutionRandomSweep)), coordinates_int, 'r')  # matplot of sweep solution

# 6.1 VehicleSwap for the SweepSolution
# list_avb = copy.deepcopy(listOfInitialVehicles)
# for r in bestSolutionRandomSweep:
#     cost_dummy, vehicle_dummy = find_cheapest_vehicle(r.customer_list, ourInstance, 100, list_avb)
#     list_avb.remove(vehicle_dummy)
# start1 = time.perf_counter()
listOfInitAvailableVehicles = vehicle_assignment(bestSolutionRandomSweep, listOfInitialVehicles, ourInstance, 0, True)  # vehicle_assignment(list_of_routes: list[Route], initial_list_of_vehicles: List[Vehicle], instance: Instance):
# time1 = time.perf_counter() - start1
# print(time1)
# start2 = time.perf_counter()
# listOfInitAvailableVehicles = vehicle_assignment(bestSolutionRandomSweep, listOfInitialVehicles, ourInstance, 100, True)
# time2 = time.perf_counter() - start2
# print(time2)

# 7. OUR ALGORITHM (DESTRUCTION + INSERTION + OPTIMIZATION + ACCEPTANCE)
solutionOur = ouralgorithm(ourInstance, bestSolutionRandomSweep, listOfInitialVehicles, listOfInitAvailableVehicles,
                           coordinates_int)
# lenOfSolutionOur = len(solutionOur)
# for i in range(lenOfSolutionOur):
#     print(f"Sum of demands of a {i} route: " + str(compute_total_demand(solutionOur[i], ourInstance)))
# print(compute_distances(solutionOur, ourInstance))
plotTSP(solutionOur, coordinates_int, 'g', False, 'No Depot Plot')
plotTSP(solutionOur, coordinates_int, 'g', True, 'Route Plot')

