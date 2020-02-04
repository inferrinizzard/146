# CMPM146 - Game AI
# P1 - Dijkstra's in a Dungeon
# By: Sean Song and Hana Cho

from p1_support import load_level, show_level, save_level_costs
from math import inf, sqrt
from heapq import heappop, heappush


def dijkstras_shortest_path(initial_position, destination, graph, adj):
    """ Searches for a minimal cost path through a graph using Dijkstra's algorithm.

    Args:
        initial_position: The initial cell from which the path extends.
        destination: The end location for the path.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        If a path exits, return a list containing all cells from initial_position to destination.
        Otherwise, return None.

    """
    q = [(0, initial_position)]  # node queue
    visited = {initial_position: (0, None)}  # dist, prev

    # while queue not empty
    while q:
        cur_dist, cur = heappop(q)  # get current
        if cur == destination:  # check success
            path = [cur]
            back = visited[cur][1]
            while back and back is not initial_position:  # backpathing
                path = [back] + path
                back = visited[back][1]
            return [initial_position] + path
        for pos, cost in adj(graph, cur):  # for each neighbour
            if cost is not inf:
                pathcost = cost + cur_dist
                if not visited.get(pos) or pathcost < visited[pos][0]:
                    visited[pos] = (pathcost, cur)
                    heappush(q, (pathcost, pos))
    return None


def dijkstras_shortest_path_to_all(initial_position, graph, adj):
    """ Calculates the minimum cost to every reachable cell in a graph from the initial_position.

    Args:
        initial_position: The initial cell from which the path extends.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        A dictionary, mapping destination cells to the cost of a path from the initial_position.
    """
    level = {**graph["spaces"],**{pos:1.0 for pos in graph["waypoints"].values()}} # recomprehend graph
    level_cost = {}
    for pos in level: # for every reachable space
        p = dijkstras_shortest_path(initial_position, pos, graph, adj) # find path
        cost = 0 if p else inf
        if p:
            for i in range(len(p)-1):
                a = p[i]
                b = p[i+1]
                cost = cost + (level[a] + level[b]) / 2 * (1 if abs(a[0]-b[0]) + abs(a[1]-b[1]) > 1 else sqrt(2)) #calc path cost
        level_cost[pos] = cost
    return level_cost


def navigation_edges(level, cell):
    """ Provides a list of adjacent cells and their respective costs from the given cell.

    Args:
        level: A loaded level, containing walls, spaces, and waypoints.
        cell: A target location.

    Returns:
        A list of tuples containing an adjacent cell's coordinates and the cost of the edge joining it and the
        originating cell.

        E.g. from (0,0):
            [((0,1), 1),
             ((1,0), 1),
             ((1,1), 1.4142135623730951),
             ... ]
    """
    neighbors = []

    # iterate over adjacent cells
    for i in range(cell[0]-1, cell[0]+2):
        for j in range(cell[1]-1, cell[1]+2):
            # if cell is not original cell
            if (i, j) != cell:
                # if cell is a wall
                if (i, j) in level['walls']:
                    cost = inf
                # if new cell is diagonal from original cell
                elif abs(i - cell[0]) > 0 and abs(j - cell[1]) > 0:
                    cost = sqrt(2) * 0.5 * \
                        (level['spaces'][(i, j)] + level['spaces'][cell])
                else:
                    cost = 0.5 * (level['spaces'][(i, j)] +
                                  level['spaces'][cell])

                neighbors.append(((i, j), cost))

    return neighbors


def test_route(filename, src_waypoint, dst_waypoint):
    """ Loads a level, searches for a path between the given waypoints, and displays the result.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        dst_waypoint: The character associated with the destination waypoint.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source and destination coordinates from the level.
    src = level['waypoints'][src_waypoint]
    dst = level['waypoints'][dst_waypoint]

    # Search for and display the path from src to dst.
    path = dijkstras_shortest_path(src, dst, level, navigation_edges)
    if path:
        show_level(level, path)
    else:
        print("No path possible!")


def cost_to_all_cells(filename, src_waypoint, output_filename):
    """ Loads a level, calculates the cost to all reachable cells from 
    src_waypoint, then saves the result in a csv file with name output_filename.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        output_filename: The filename for the output csv file.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source coordinates from the level.
    src = level['waypoints'][src_waypoint]

    # Calculate the cost to all reachable cells from src and save to a csv file.
    costs_to_all_cells = dijkstras_shortest_path_to_all(
        src, level, navigation_edges)
    save_level_costs(level, costs_to_all_cells, output_filename)


if __name__ == '__main__':
    filename, src_waypoint, dst_waypoint = 'example.txt', 'a', 'e'

    # Use this function call to find the route between two waypoints.
    test_route(filename, src_waypoint, dst_waypoint)

    # Use this function to calculate the cost to all reachable cells from an origin point.
    cost_to_all_cells(filename, src_waypoint, 'my_costs.csv')
