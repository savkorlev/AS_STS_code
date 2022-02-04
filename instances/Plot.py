# requires matplotlib package (https://matplotlib.org)
# Note: PyPy might have problems with this lib
import copy
import random
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np
import seaborn as sns


# coordinates for matplot START
def create_list_int_coordinates(df_nodes) -> list():  # didnt work with floats so I turned the coordinates into int
    LonInt = []
    Lon = list(df_nodes.loc[:, "Lon"])
    for lon in Lon:
        lon = lon * 10000000  # probably the stupidest way to turn a flot into an int... sorry - Christopher
        lon = int(lon)
        LonInt.append(lon)

    LatInt = []
    Lat = list(df_nodes.loc[:, "Lat"])
    for lat in Lat:
        lat = lat * 10000000
        lat = int(lat)
        LatInt.append(lat)

    coordinates_int = []
    for i in range(len(LonInt)):
        cord_int = (LonInt[i], LatInt[i])
        coordinates_int.append(cord_int)

    return coordinates_int


# coordinates for matplot END


# def plotTSP(routes, points, color, show_depot=True, title='ArcPlot'):
#     """
#     routes: List of lists with the different orders in which the nodes are visited
#     points: coordinates for the different nodes
#     color: currently not used
#     show_depot: deletes depot from all paths if false
#     """
#     plt.figure(1, figsize=(10, 9))
#     plt.title(title)
# 
#     path = copy.deepcopy(routes)  # need to deepcopy so we dont destroy the real route by drawing them without depot
# 
#     if not show_depot:  # allows us to draw routes without depot, which gives a clearer picture
#         for r in path:
#             while 0 in r:
#                 r.remove(0)
# 
#     a_scale = 30000  # size of the arrowhead
# 
#     n = len(path)
#     colorlist = sns.color_palette("husl", n)
# 
#     counter_route = 0
#     for r in range(len(path)):
#         counter_route += 1
#         x = []
#         y = []
#         # color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)) # sets a random color, this could be smarter
#         color = colorlist[counter_route - 1]
#         for i in path[r]:
#             x.append(points[i][0])
#             y.append(points[i][1])
#         for i in range(0, len(x) - 1):  # draw the route
#             if i == 0:
#                 plt.arrow(x[i], y[i], (x[i + 1] - x[i]), (y[i + 1] - y[i]), head_width=a_scale,
#                           color=color, length_includes_head=True, label="route " + str(counter_route))
#             else:
#                 plt.arrow(x[i], y[i], (x[i + 1] - x[i]), (y[i + 1] - y[i]), head_width=a_scale,
#                           color=color, length_includes_head=True)
# 
#         plt.plot(x, y, "co", markersize=4)  # draw the nodes. If I change the color, everything breaks...
# 
#     plt.legend(loc="upper left")
#     plt.show()
    
    
def plotVRP(solution, points, show_depot=True, title='ArcPlot'):
    """
    routes: List of lists with the different orders in which the nodes are visited
    points: coordinates for the different nodes
    color: currently not used
    show_depot: deletes depot from all paths if false
    """
    plt.figure(1, figsize=(10, 9))
    plt.title(title)

    # routes = list(map(lambda x: x.customer_list, solution))

    path = copy.deepcopy(solution)  # need to deepcopy so we dont destroy the real route by drawing them without depot

    if not show_depot:  # allows us to draw routes without depot, which gives a clearer picture
        for r in path:
            while 0 in r.customer_list:
                r.customer_list.remove(0)

    a_scale = 30000  # size of the arrowhead

    n = len(path)
    colorlist = sns.color_palette("husl", n)

    counter_route = 0
    for r in path:
        counter_route += 1
        x = []
        y = []
        # color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)) # sets a random color, this could be smarter
        color = colorlist[counter_route - 1]
        for i in r.customer_list:
            x.append(points[i][0])
            y.append(points[i][1])
        for i in range(0, len(x) - 1):  # draw the route
            if i == 0:
                plt.arrow(x[i], y[i], (x[i + 1] - x[i]), (y[i + 1] - y[i]), head_width=a_scale,
                          color=color, length_includes_head=True, label="route " + str(counter_route) + ' - ' + str(r.vehicle.type))
            else:
                plt.arrow(x[i], y[i], (x[i + 1] - x[i]), (y[i + 1] - y[i]), head_width=a_scale,
                          color=color, length_includes_head=True)

        plt.plot(x, y, "co", markersize=4)  # draw the nodes. If I change the color, everything breaks...

    plt.legend(loc="upper left")
    plt.show()


def plotGraph(points, title: str, color='g'):
    x = []
    y = []

    for i in range(len(points)):
        x.append(points[i][0])
        y.append(points[i][1])

    plt.plot(x, y, "co", markersize=3)  # draw the nodes. If I change the color, everything breaks...
    plt.title(title)

    plt.show()


def plotSubplots(points, points2, title='SubPlots'):
    plt.style.use('seaborn-whitegrid')

    x = []
    y = []

    for i in range(len(points)):
        x.append(points[i][0])
        y.append(points[i][1])

    x2 = []
    y2 = []

    for i in range(len(points2)):
        x2.append(points2[i][0])
        y2.append(points2[i][1])

    fig = plt.figure(1, figsize=(10, 9))
    ax1 = fig.add_subplot(211)
    plt.plot(x, y, "co", markersize=2)  # draw the nodes.

    ax2 = fig.add_subplot(212, sharex=ax1)
    plt.plot(x2, y2, color='red', markersize=3)

    # plt.setp(ax1.get_xticklabels(), visible=False)  # hide labels
    plt.title(title)
    fig.subplots_adjust(hspace=0)  # remove vertical space between subplots

    plt.show()


def plot3Subplots(points, points2, points3, title='SubPlots'):
    plt.style.use('seaborn-whitegrid')

    x = []
    y = []

    for i in range(len(points)):
        x.append(points[i][0])
        y.append(points[i][1])

    x2_green = []
    y2_green = []
    x2_red = []
    y2_red = []

    for i in range(len(points2)):
        if points2[i][2]:  # feasible solutions
            x2_green.append(points2[i][0])
            y2_green.append(points2[i][1])
        else:
            x2_red.append(points2[i][0])
            y2_red.append(points2[i][1])

    x3 = []
    y3 = []

    for i in range(len(points3)):
        x3.append(points3[i][0])
        y3.append(points3[i][1])

    fig = plt.figure(1, figsize=(10, 9))
    ax1 = fig.add_subplot(211)
    plt.plot(x, y, "o", color='c', markersize=2)  # draw the nodes.
    plt.plot(x2_red, y2_red, "d", color='orange', markersize=4)  # draw best solutions in red/green depending on feasibility
    plt.plot(x2_green, y2_green, "d", color='blue', markersize=5)

    ax2 = fig.add_subplot(212, sharex=ax1)
    plt.plot(x3, y3, color='red', markersize=3)

    # plt.setp(ax1.get_xticklabels(), visible=False)  # hide labels
    plt.title(title)
    fig.subplots_adjust(hspace=0)  # remove vertical space between subplots

    plt.show()


""" draw function from live coding. I could not get it to work - Christopher"""
# # draw nodes and routes
# # requires list of routes R = [[0,..,0],..], i.e., list of list of visits
# def draw_routes(R, nodes):
#     # set color scheme
#     # https://matplotlib.org/3.2.1/gallery/color/colormap_reference.html
#     colors = plt.cm.get_cmap('tab10', len(R))
# 
#     fig, ax = plt.subplots()
# 
#     for r_idx, r in enumerate(R):
#         path = list()
#         for i in range(len(r)):
#             path.append((nodes[r[i]]['x'], nodes[r[i]]['y']))
#             # path.append((nodes[i][0], nodes[i][1]))
# 
#         # plot control points and connecting lines
#         x, y = zip(*path)
#         line, = ax.plot(x, y, 'o-', color=colors(r_idx))
# 
#     ax.plot(nodes[0]['x'], nodes[0]['y'], 'ks')
# 
#     # ax.grid()
#     ax.axis('equal')
# 
#     # hide axis labels
#     plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
#     plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
# 
#     # hide bounding box
#     # for pos in ['right', 'top', 'bottom', 'left']:
#     #     plt.gca().spines[pos].set_visible(False)
# 
#     plt.show()
