import os
import pandas as pd

# os.chdir('C:/Users/Christopher/PycharmProjects/AS_STS_code')

df_NewYork_1_nodes = pd.read_csv("data/NewYork.1.nodes", sep=' ')
df_NewYork_2_nodes = pd.read_csv("data/NewYork.2.nodes", sep=' ')
df_NewYork_routes = pd.read_csv("data/NewYork.routes", sep=' ')
df_Paris_nodes = pd.read_csv("data/Paris.nodes", sep=' ')
df_Paris_routes = pd.read_csv("data/Paris.routes", sep=' ')
df_Shanghai_nodes = pd.read_csv("data/Shanghai.nodes", sep=' ')
df_Shanghai_routes = pd.read_csv("data/Shanghai.routes", sep=' ')

# print(df_NewYork_1_nodes)
# print(df_NewYork_2_nodes)
# print(df_NewYork_routes)
# print(df_Paris_nodes)
# print(df_Paris_routes)
# print(df_Shanghai_nodes)
# print(df_Shanghai_routes)

print(df_NewYork_1_nodes.columns)

# .loc[] - access the data by the name
print(df_NewYork_1_nodes.loc[:, "Duration"])  #select all rows and the "Duration" column
print(type(df_NewYork_1_nodes.loc[:, "Duration"]))  #return type - Series

print(df_NewYork_1_nodes.loc[:, ["Duration"]])  #select all rows and the "Duration" column
print(type(df_NewYork_1_nodes.loc[:, ["Duration"]]))  #return type - DataFrame

# .iloc[] - access the data by its number
print(df_NewYork_1_nodes.iloc[:, 2])  #select all rows and the third column
print(df_NewYork_1_nodes.iloc[2, 2])  #select the third row and the third column


print('test commit')