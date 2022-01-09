# requires matplotlib package (https://matplotlib.org)
# Note: PyPy might have problems with this lib
import random

import matplotlib.pyplot as plt


def plotTSP(path, points):
    """
    path: List of lists with the different orders in which the nodes are visited
    points: coordinates for the different nodes
    num_iters: number of paths that are in the path list

    """

    # Unpack the primary TSP path and transform it into a list of ordered
    # coordinates
    a_scale = 1
    color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))

    x = []
    y = []


    for r in range(len(path)):
        # color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
        for i in path[r]:
            x.append(points[i][0])
            y.append(points[i][1])

    plt.plot(x, y, 'co')
    plt.arrow(x[-1], y[-1], (x[0] - x[-1]), (y[0] - y[-1]), head_width=a_scale,
              color=color, length_includes_head=True)
    for i in range(0, len(x) - 1):
        plt.arrow(x[i], y[i], (x[i + 1] - x[i]), (y[i + 1] - y[i]), head_width=a_scale,
                  color=color, length_includes_head=True)
    plt.show()




    # a_scale = float(max(y)) / float(100) # Set a scale for the arrow heads (there should be a reasonable default for this, WTF?)


    # Draw the primary path for the TSP problem
    # plt.arrow(x[-1], y[-1], (x[0] - x[-1]), (y[0] - y[-1]), head_width=a_scale,
    #           color=color, length_includes_head=True)
    # for i in range(0, len(x) - 1):
    #     plt.arrow(x[i], y[i], (x[i + 1] - x[i]), (y[i + 1] - y[i]), head_width=a_scale,
    #               color=color, length_includes_head=True)

    # Set axis too slitghtly larger than the set of x and y
    # plt.xlim(min(x)*0.9, max(x) * 1.1)
    # plt.ylim(min(y)*0.9, max(y) * 1.1)
    plt.show()


# draw nodes and routes
# requires list of routes R = [[0,..,0],..], i.e., list of list of visits
def draw_routes(R, nodes):
    # set color scheme
    # https://matplotlib.org/3.2.1/gallery/color/colormap_reference.html
    colors = plt.cm.get_cmap('tab10', len(R))

    fig, ax = plt.subplots()

    for r_idx, r in enumerate(R):
        path = list()
        for i in range(len(r)):
            path.append((nodes[r[i]]['x'], nodes[r[i]]['y']))
            #path.append((nodes[i][0], nodes[i][1]))

        # plot control points and connecting lines
        x, y = zip(*path)
        line, = ax.plot(x, y, 'o-', color=colors(r_idx))

    ax.plot(nodes[0]['x'], nodes[0]['y'], 'ks')

    # ax.grid()
    ax.axis('equal')

    # hide axis labels
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)

    # hide bounding box
    # for pos in ['right', 'top', 'bottom', 'left']:
    #     plt.gca().spines[pos].set_visible(False)

    plt.show()

