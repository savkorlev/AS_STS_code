import pandas as pd

from instances.Construction import sort_customers_by_sweep, ouralgorithm, checkForAcceptance
from instances.LocalSearch import find_first_improvement_2Opt, find_first_improvement_relocate, \
    find_first_improvement_exchange
from instances.Trucks import TruckOne, TruckTwo
from instances.Utils import Instance, next_fit_heuristic_naive, compute_distances, next_fit_heuristic, is_feasible, \
    compute_total_demand

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
truck1 = TruckOne(1500)
truck2 = TruckTwo(1200)

# 3. CREATING TEST DATASET AND ATTRIBUTES OF FUTURE INSTANCE
testDimension = 20

test_df_Paris_nodes = df_Paris_nodes.iloc[:20, :]                   # select elements from D0 to C19 in nodes
test_df_Paris_routes = df_Paris_routes.iloc[:2260, :]               # select elements from D0 to C19 in routes
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
ourInstance = Instance(testDimension, truck1.capacity, testDemandParis, testParisDistances, coordinates)

# 5. SIMPLE SOLUTION
solution = next_fit_heuristic_naive(ourInstance)
# Update: by adding an 'f' before a string, you allow for so-called string interpolation, i.e., you can use
#  {} to access variables from the outer scope which will be inserted at this point in the string.
print(f"Next-Fit-Heuristic | #Vehicles: {len(solution)}, distance: {compute_distances(solution, ourInstance)}")

# 6. SWEEP HEURISTIC
solutionSweep = next_fit_heuristic(sort_customers_by_sweep(ourInstance), ourInstance)
print(f"Sweep Heuristic | #Vehicles: {len(solutionSweep)}, distance: {compute_distances(solutionSweep, ourInstance)}, is_feasible: {is_feasible(solutionSweep, ourInstance)}")

# 7. DESTRUCTION & INSERTION & OPTIMIZATION
solutionOur = ouralgorithm(ourInstance, solutionSweep, find_first_improvement_2Opt)
lenOfSolutionOur = len(solutionOur)
for i in range(lenOfSolutionOur):
    print(f"Sum of demands of an {i}-th route: " + str(compute_total_demand(solutionOur[i], ourInstance)))

# 8. CHECK FOR ACCEPTANCE
checkForAcceptance(solutionSweep, ourInstance)
