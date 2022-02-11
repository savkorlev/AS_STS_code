import argparse
import datetime
import sys
import copy
import time

import pandas as pd

from instances.Construction import ouralgorithm
from instances.Intialization import random_sweep
from instances.Trucks import create_vehicles
from instances.Utils import Instance, vehicle_assignment, solution_cost, find_cheapest_vehicle, Instance_tune
from instances.Plot import plotVRP, inner_city_check

import os
# os.chdir('C:/Users/Евгений/Desktop/TUM/WS 2021-2022/Advanced Seminar Sustainable Transportation Systems/AS_STS_code')
# os.chdir('C:/Users/Maximilian Sammer/PycharmProjects/AS_STS_code/')
# os.chdir('/Users/tuminyu/Desktop/Cory/TUM Master/Advanced Seminar/Code/Project')
# os.chdir('C:/Users/Christopher/PycharmProjects/AS_STS_code/')

### may come in handy later on:
# from src import TSPLibReader
# instance = TSPLibReader.read("instances/carModel1.vrp") //using .vrp
###

# 0. ENTER THE CITY (NewYork, Paris, Shanghai)
city = "Shanghai"
# set the # of vehicles available to Sweep and Algorithm
numI_Atego = 20
numI_VWTrans = 20
numI_VWCaddy = 20
numI_DeFuso = 20
numI_ScooterL = 20
numI_ScooterS = 20
numI_eCargoBike = 20

# set fixed costs on/off
fixed_cost_active = True  # sets fixed costs active for all vehicles
tax_ins_active = True  # sets taxes and insurance active. Makes fixed costs for all non-leased vehicles ~90% higher (20% for bike).

# set demand_factor
kg_factor = 1
# set volume_factor
vol_factor = 1
# set city cost lvl: 'none', 'low', 'medium', 'high', 'ban'
city_cost_level = 'medium'

# set the run parameters
perform_dict = {}
params_dict = {
    'max_iterations': [5000, 5000, 5000],
    'init_temp': [0.1],
    'temp_target_percentage': [0.025],
    'temp_target_iteration': [1.2],
    'freeze_period_length': [0.02],
    'destroy_random_ub': [0.12],
    'destroy_expensive_ub': [0.1],
    'destroy_route_ub': [0.5],
    'destroy_related_ub': [0.12],
    'max_weight': [5000],  # Botch: if this is set to 5001, we activate Vehicle_Assignment after Destruction
    'min_weight': [10],
    'reduce_step': [4],
    'step_penalty': [1],
}


# 1. LOADING THE DATA

# df_NewYork_1_nodes = pd.read_csv("data/NewYork.1.nodes", sep=' ')
# df_NewYork_2_nodes = pd.read_csv("data/NewYork.2.nodes", sep=' ')
if city == "NewYork":
    df_nodes = pd.read_csv("data/NewYork.nodes", sep=' ')
    df_nodes["Duration"] = pd.to_timedelta(df_nodes["Duration"]).dt.total_seconds() / 60  # converting duration column to floats instead of strings
    df_routes = pd.read_csv("data/NewYork.routes", sep=' ')
    df_routes["Duration[s]"] = pd.to_timedelta(df_routes["Duration[s]"]).dt.total_seconds() / 60  # converting duration column to floats instead of strings
if city == "Paris":
    df_nodes = pd.read_csv("data/Paris.nodes", sep=' ')
    df_nodes["Duration"] = pd.to_timedelta(df_nodes["Duration"]).dt.total_seconds() / 60  # converting duration column to floats instead of strings
    df_routes = pd.read_csv("data/Paris.routes", sep=' ')
    df_routes["Duration[s]"] = pd.to_timedelta(df_routes["Duration[s]"]).dt.total_seconds() / 60  # converting duration column to floats instead of strings
if city == "Shanghai":
    df_nodes = pd.read_csv("data/Shanghai.nodes", sep=' ')
    df_nodes["Duration"] = pd.to_timedelta(df_nodes["Duration"]).dt.total_seconds() / 60  # converting duration column to floats instead of strings
    df_routes = pd.read_csv("data/Shanghai.routes", sep=' ')
    df_routes["Duration[s]"] = pd.to_timedelta(df_routes["Duration[s]"]).dt.total_seconds() / 60  # converting duration column to floats instead of strings

# 2. CREATING TEST DATASET AND ATTRIBUTES OF FUTURE INSTANCE
# set testDimension to 1 more than customers
testDimension = len(df_nodes)  # change this to use more or less customers of the data set. Max for Paris is 112. Also need to change the iloc for the nodes file
# 1 + either 19, 39 or 112

# DON'T FORGET TO SET MORE VEHICLES IF YOU HAVE MORE CUSTOMERS

if testDimension == 20:
    df_nodes_subset = df_nodes.iloc[:20, :]  # select elements from D0 to C19 in nodes
    df_routes_subset = df_routes.iloc[:2260, :]  # select elements from D0 to C19 in routes
if testDimension == 40:
    df_nodes_subset = df_nodes.iloc[:40, :]  # select elements from D0 to C40 in nodes
    df_routes_subset = df_routes.iloc[:4633, :]  # select elements from D0 to C40 in routes
if testDimension == len(df_nodes):
    df_nodes_subset = df_nodes  # select all elements (choose if 112 customers)
    df_routes_subset = df_routes  # select all elements (choose if 112 customers)
# print(df_nodes_subset)
# print(df_routes_subset)

subsetDemand = list(df_nodes_subset.loc[:, "Demand[kg]"])  # select demand column (in kg) and convert it to a list
# print(subsetDemand)

if kg_factor != 1:
    print(f"original demand kg: {subsetDemand}")
    for i in range(len(subsetDemand)):
        subsetDemand[i] = round(subsetDemand[i] * kg_factor)
    print(f"kg factor: {kg_factor}")
    print(f"changed demand kg: {subsetDemand}\n")

subsetVolume = list(df_nodes_subset.loc[:, "Demand[m^3*10^-3]"])  # select demand column (in volume) and convert it to a list
if vol_factor != 1:
    print(f"original volume: {subsetVolume}")
    for i in range(len(subsetVolume)):
        subsetVolume[i] = round(subsetVolume[i] * kg_factor)
    print(f"volume factor: {vol_factor}")
    print(f"changed volume: {subsetVolume}\n")

# print(subsetVolume)
subsetDuration = list(df_nodes_subset.loc[:, "Duration"])  # select duration column (in volume) and convert it to a list
# print(subsetDuration)

subsetDistances = {}  # the purpose of the following up loop is
for row, content in df_routes_subset.iterrows():  # to create tuples with distances from one Id
    key = (int(content[0][1:]), int(content[1][1:]))  # to another
    subsetDistances[key] = content[2]
# print(subsetDistances)

subsetDistanceInside = {}  # the purpose of the following up loop is
for row, content in df_routes_subset.iterrows():  # to create tuples with distances from one Id
    key = (int(content[0][1:]), int(content[1][1:]))  # to another inside the city
    subsetDistanceInside[key] = content[3]
# print(subsetDistanceInside)

subsetDistanceOutside = {}  # the purpose of the following up loop is
for row, content in df_routes_subset.iterrows():  # to create tuples with distances from one Id
    key = (int(content[0][1:]), int(content[1][1:]))  # to another outside the city
    subsetDistanceOutside[key] = content[4]
# print(subsetDistanceOutside)

subsetArcDuration = {}  # the purpose of the following up loop is
for row, content in df_routes_subset.iterrows():  # to create tuples with durations from one Id
    key = (int(content[0][1:]), int(content[1][1:]))  # to another inside the city
    subsetArcDuration[key] = content[5]
# print(subsetArcDuration)

coordinates = []
for row, content in df_nodes_subset.iterrows():
    coordinate = (content[1], content[2])
    coordinates.append(coordinate)
print(coordinates)

outside_dictionary = inner_city_check(df_nodes_subset, subsetDistanceInside, subsetDistanceOutside)
# print(outside_dictionary)

# coordinates for matplot
# coordinates_int = create_list_int_coordinates(df_nodes_subset)
# print(coordinates_int)
# coordinates_float = create_list_float_coordinates(df_nodes_subset)
# print(coordinates_float)
# 3. CREATING OUR VEHICLES
# create vehicles via function in Trucks.py-file
listOfInitialVehicles = create_vehicles(city, city_cost_level, numI_Atego, numI_VWTrans, numI_VWCaddy, numI_DeFuso, numI_ScooterL,
                                        numI_ScooterS, numI_eCargoBike, fixed_cost_active, tax_ins_active)
print(f"List of initial Vehicle payloads_kg: {list(map(lambda x: x.payload_kg, listOfInitialVehicles))}")

# test feasibility of our vehicle assignment. Need enough capacity to carry all demand.
sumOfDemand = sum(subsetDemand)
sumOfCapacity = numI_Atego * 2800 + numI_VWTrans * 883 + numI_VWCaddy * 670 + numI_DeFuso * 2800 + numI_ScooterL * 905 + numI_ScooterS * 720 + numI_eCargoBike * 100
if sumOfCapacity < sumOfDemand:
    print(f"Not enough Capacity ({sumOfCapacity}) for Demand ({sumOfDemand})")
    sys.exit()

# # 5. CREATING INSTANCE
""" alter code für einzelnen Lauf ohne Parameter"""
# ourInstance = Instance(testDimension, listOfInitialVehicles, testDemandParis, testDemandParisVolume, testParisCustomerDuration,
#                        testParisDistances, testParisDistancesInside, testParisDistancesOutside, testParisArcDuration, coordinates)
# 
# # 6. SWEEP HEURISTIC
# """ The Sweep Heuristic will only work if we have enough payload_kg capacity to assign all customers to feasible [kg] routes"""
# bestCostRandomSweep = 10e10
# for i in range(10): # we run the sweep heuristic multiple times with different starting angles to get a good starting solution
#     tempSolutionRandomSweep = random_sweep(ourInstance, listOfInitialVehicles)
#     tempCost = solution_cost(tempSolutionRandomSweep, ourInstance, 0, True)
#     # print(f"Rand Sweep Heuristic, temp distance: {compute_distances(tempSolutionRandomSweep, ourInstance)}")
#     if tempCost < bestCostRandomSweep:
#         bestSolutionRandomSweep = copy.deepcopy(tempSolutionRandomSweep)
#         bestCostRandomSweep = tempCost
# print(f"Rand Sweep Heuristic, #Vehicles: {len(bestSolutionRandomSweep)}, cost: {bestCostRandomSweep}")
# 
# 
# # 6.1 VehicleSwap for the SweepSolution
# listOfInitAvailableVehicles = vehicle_assignment(bestSolutionRandomSweep, listOfInitialVehicles, ourInstance, 0, True)  # vehicle_assignment(list_of_routes: list[Route], initial_list_of_vehicles: List[Vehicle], instance: Instance):
# 
# # 7. OUR ALGORITHM (DESTRUCTION + INSERTION + OPTIMIZATION + ACCEPTANCE)
# solutionOur = ouralgorithm(ourInstance, bestSolutionRandomSweep, listOfInitialVehicles, listOfInitAvailableVehicles,
#                            coordinates)
# print(f"numI_Atego: {numI_Atego,}, numI_VWTrans: {numI_VWTrans}, numI_VWCaddy: {numI_VWCaddy}, numI_DeFuso: {numI_DeFuso}, numI_ScooterL: {numI_ScooterL}, numI_ScooterS: {numI_ScooterS}, numI_eCargoBike: {numI_eCargoBike}")


# 8. Parameter Analysis

# Design Freeze - 2022-02-07 - 14:00
# params_dict = {
#     'max_iterations': [10000],
#     'init_temp': [0.1],
#     'temp_target_percentage': [0.025],
#     'temp_target_iteration': [1.2],
#     'freeze_period_length': [0.02],
#     'destroy_random_ub': [0.12],
#     'destroy_expensive_ub': [0.1],
#     'destroy_route_ub': [1],
#     'destroy_related_ub': [0.12],
#     'max_weight': [5000],
#     'min_weight': [10],
#     'reduce_step': [4],
#     'step_penalty': [1],
# }


n = 0
for a in params_dict['max_iterations']:
    for b in params_dict['init_temp']:
        for c in params_dict['temp_target_percentage']:
            for d in params_dict['temp_target_iteration']:
                for e in params_dict['freeze_period_length']:
                    for f in params_dict['destroy_random_ub']:
                        for g in params_dict['destroy_expensive_ub']:
                            for h in params_dict['destroy_route_ub']:
                                for i_par in params_dict['destroy_related_ub']:
                                    for j in params_dict['max_weight']:
                                        for k in params_dict['min_weight']:
                                            for l in params_dict['reduce_step']:
                                                for m in params_dict['step_penalty']:
                                                    parser = argparse.ArgumentParser()
                                                    parser.add_argument('--' + str('max_iterations'), default=a)
                                                    parser.add_argument('--' + str('init_temp'), default=b)
                                                    parser.add_argument('--' + str('temp_target_percentage'), default=c)
                                                    parser.add_argument('--' + str('temp_target_iteration'), default=d)
                                                    parser.add_argument('--' + str('freeze_period_length'), default=e)
                                                    parser.add_argument('--' + str('destroy_random_ub'), default=f)
                                                    parser.add_argument('--' + str('destroy_expensive_ub'), default=g)
                                                    parser.add_argument('--' + str('destroy_route_ub'), default=h)
                                                    parser.add_argument('--' + str('destroy_related_ub'), default=i_par)
                                                    parser.add_argument('--' + str('max_weight'), default=j)
                                                    parser.add_argument('--' + str('min_weight'), default=k)
                                                    parser.add_argument('--' + str('reduce_step'), default=l)
                                                    parser.add_argument('--' + str('step_penalty'), default=m)
                                                    args = parser.parse_args()
                                                    ourInstance = Instance_tune(testDimension, listOfInitialVehicles,
                                                                                subsetDemand,
                                                                                subsetVolume,
                                                                                subsetDuration,
                                                                                subsetDistances,
                                                                                subsetDistanceInside,
                                                                                subsetDistanceOutside,
                                                                                subsetArcDuration, coordinates,
                                                                                args)
                                                    bestCostRandomSweep = 10e10
                                                    start_time_run = time.perf_counter()
                                                    for i in range(10):
                                                        tempSolutionRandomSweep = random_sweep(ourInstance,
                                                                                               listOfInitialVehicles)
                                                        tempCost = solution_cost(tempSolutionRandomSweep, ourInstance,
                                                                                 0, True)
                                                        # print(f"Rand Sweep Heuristic, temp distance: {compute_distances(tempSolutionRandomSweep, ourInstance)}")
                                                        if tempCost < bestCostRandomSweep:
                                                            bestSolutionRandomSweep = copy.deepcopy(
                                                                tempSolutionRandomSweep)
                                                            bestCostRandomSweep = tempCost
                                                    listOfInitAvailableVehicles = vehicle_assignment(
                                                        bestSolutionRandomSweep,
                                                        listOfInitialVehicles, ourInstance,
                                                        0, True)
                                                    sol, final_cost, feasible = ouralgorithm(ourInstance, bestSolutionRandomSweep,
                                                                                   listOfInitialVehicles,
                                                                                   listOfInitAvailableVehicles,
                                                                                   coordinates)
                                                    end_time_run = time.perf_counter()
                                                    runtime_run = end_time_run - start_time_run
                                                    print(
                                                        f"numI_Atego: {numI_Atego,}, numI_VWTrans: {numI_VWTrans}, numI_VWCaddy: {numI_VWCaddy}, numI_DeFuso: {numI_DeFuso}, numI_ScooterL: {numI_ScooterL}, numI_ScooterS: {numI_ScooterS}, numI_eCargoBike: {numI_eCargoBike}")
                                                    no_depot_title = 'No Depot Plot ' + str(n)
                                                    depot_title = 'Route Plot in Permutation ' + str(n)
                                                    # plotVRP(sol, coordinates, False, no_depot_title)
                                                    plotVRP(sol, coordinates, outside_dictionary, True, depot_title)

                                                    perform_dict[n] = [a, b, c, d, e, f, g, h, i_par, j, k, l, m, feasible, fixed_cost_active, tax_ins_active, final_cost, runtime_run]
                                                    n += 1

summary_performance = pd.DataFrame.from_dict(perform_dict, orient='index', columns=list(params_dict.keys()) + ['feasible'] + ['fixed costs'] +['tax+ins'] + ['cost'] + ['runtime in s'])
print()
print(summary_performance)

date_string = str(datetime.datetime.now())
date_string = date_string.replace(":", "-")
summary_performance.to_csv(date_string[:16] + ' - parameter_analysis.csv')

os.system("start C:/Users/Christopher/PycharmProjects/AS_STS_code/Doorbell.wav")
