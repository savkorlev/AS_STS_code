# START OF DATA IMPORTING
import pandas as pd
from instances.Construction import sort_customers_by_sweep, ouralgorithm, checkForAcceptance
from instances.LocalSearch import find_first_improvement_2Opt, find_first_improvement_relocate, \
    find_first_improvement_exchange
from instances.Trucks import TruckOne
from instances.Utils import Instance, next_fit_heuristic_naive, compute_distances, next_fit_heuristic, is_feasible, \
    compute_total_demand
df_NewYork_1_nodes = pd.read_csv("data/NewYork.1.nodes", sep=' ')
df_NewYork_2_nodes = pd.read_csv("data/NewYork.2.nodes", sep=' ')
df_NewYork_routes = pd.read_csv("data/NewYork.routes", sep=' ')
df_Paris_nodes = pd.read_csv("data/Paris.nodes", sep=' ')
df_Paris_routes = pd.read_csv("data/Paris.routes", sep=' ')
df_Shanghai_nodes = pd.read_csv("data/Shanghai.nodes", sep=' ')
df_Shanghai_routes = pd.read_csv("data/Shanghai.routes", sep=' ')
truck1 = TruckOne(1500)
testDimension = 20
test_df_Paris_nodes = df_Paris_nodes.iloc[:20, :]                   # select elements from D0 to C19 in nodes
test_df_Paris_routes = df_Paris_routes.iloc[:2260, :]               # select elements from D0 to C19 in routes
testDemandParis = list(test_df_Paris_nodes.loc[:, "Demand[kg]"])    # select demand column and convert it to a list
testParisDistances = {}                                             # the purpose of the following up loop is
for row, content in test_df_Paris_routes.iterrows():                # to create tuples with distances from one Id
    key = (int(content[0][1:]), int(content[1][1:]))                # to another
    testParisDistances[key] = content[2]
coordinates = []
for row, content in test_df_Paris_nodes.iterrows():
    coordinate = (content[1], content[2])
    coordinates.append(coordinate)
ourInstance = Instance(testDimension, truck1.capacity, testDemandParis, testParisDistances, coordinates)
# END OF DATA IMPORTING


# TESTING

# ERROR. TypeError: 'int' object is not subscriptable. Line with .insert(). Data that leads to error:
# solution: [[0, 19, 10, 18, 0], [0, 3, 5, 12, 0], [0, 6, 17, 7, 0], [0, 15, 16, 1, 0], [0, 13, 8, 11, 0], [0, 14, 4, 0], [0, 9, 2, 0]]
# listAfterDestrucion: [[0, 10, 0], [0, 3, 5, 12, 0], [0, 6, 17, 7, 0], [0, 15, 16, 1, 0], [0, 13, 8, 0], [0, 14, 4, 0], [0, 2, 0]]
# listOfRemoved: [9, 18, 11, 19]

# START OF INSERTION PHASE
testSolution = [[0, 19, 10, 18, 0], [0, 3, 5, 12, 0], [0, 6, 17, 7, 0], [0, 15, 16, 1, 0], [0, 13, 8, 11, 0], [0, 14, 4, 0], [0, 9, 2, 0]]
testListAfterDestrucion = [[0, 18, 10, 19, 0], [0, 3, 5, 12, 0], [0, 6, 17, 7, 0], [0, 15, 16, 1, 0], [0, 13, 8, 0], [0, 14, 4, 0], [0, 2, 11, 0]]
testListOfRemoved = [9]
while len(testListOfRemoved) > 0:
    bestInsertionDistance = 10000
    bestPosition = 0
    bestCustomer = 0
    for customerIndex in range(len(testListOfRemoved)):  # iterating over list of removed customers
        for i in range(len(testListAfterDestrucion)):  # iterating over routes in listAfterDestruction
            for j in range(len(testListAfterDestrucion[i]) - 1):  # iterating over positions in a route
                keyNegative = (testListAfterDestrucion[i][j], testListAfterDestrucion[i][j + 1])
                key1Positive = (testListAfterDestrucion[i][j], testListOfRemoved[customerIndex])
                key2Positive = (testListOfRemoved[customerIndex], testListAfterDestrucion[i][j + 1])
                insertionDistance = ourInstance.d[key1Positive] + ourInstance.d[key2Positive] - ourInstance.d[keyNegative]  # calculation of insertion distance
                if (insertionDistance < bestInsertionDistance) & (compute_total_demand(testListAfterDestrucion[i], ourInstance) + ourInstance.q[testListOfRemoved[customerIndex]] < ourInstance.Q):  # checking both conditions, first - lowest distance, second - total demand after insertion must be lower than our truck's capacity
                    bestInsertionDistance = insertionDistance
                    bestPosition = (i, j + 1)
                    bestCustomer = testListOfRemoved[customerIndex]
    if bestInsertionDistance != 10000:
        testListAfterDestrucion[bestPosition[0]].insert(bestPosition[1], bestCustomer)  # insert bestCustomer to the best feasible route for them
    else:
        bestCustomer = testListOfRemoved[0]
        listToAppend = [0, bestCustomer, 0]
        testListAfterDestrucion.append(listToAppend)
    testListOfRemoved.remove(bestCustomer)  # delete current bestCustomer from a list of removed customers
print(f"Routes after insertion: {testListAfterDestrucion}")
# END OF INSERTION PHASE

print(compute_total_demand(testListAfterDestrucion[0], ourInstance))
print(compute_total_demand(testListAfterDestrucion[1], ourInstance))
print(compute_total_demand(testListAfterDestrucion[2], ourInstance))
print(compute_total_demand(testListAfterDestrucion[3], ourInstance))
print(compute_total_demand(testListAfterDestrucion[4], ourInstance))
print(compute_total_demand(testListAfterDestrucion[5], ourInstance))
print(compute_total_demand(testListAfterDestrucion[6], ourInstance))
print(compute_total_demand(testListAfterDestrucion[7], ourInstance))
