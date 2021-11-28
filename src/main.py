import pandas as pd

df_NewYork_1_nodes = pd.read_csv("data/NewYork.1.nodes.csv", sep=' ')
df_NewYork_2_nodes = pd.read_csv("data/NewYork.2.nodes.csv", sep=' ')
df_NewYork_routes = pd.read_csv("data/NewYork.routes.csv", sep=' ')
df_Paris_nodes = pd.read_csv("data/Paris.nodes.csv", sep=' ')
df_Paris_routes = pd.read_csv("data/Paris.routes.csv", sep=' ')
df_Shanghai_nodes = pd.read_csv("data/Shanghai.nodes.csv", sep=' ')
df_Shanghai_routes = pd.read_csv("data/Shanghai.routes.csv", sep=' ')

print(df_NewYork_1_nodes)
print(df_NewYork_2_nodes)
print(df_NewYork_routes)
print(df_Paris_nodes)
print(df_Paris_routes)
print(df_Shanghai_nodes)
print(df_Shanghai_routes)

list(df_NewYork_1_nodes.columns)
print(df_NewYork_1_nodes["Duration"])
