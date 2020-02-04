from heapq import heapify, heappush
from math import inf


def find_path(source_point, destination_point, mesh):
    """
    Searches for a path from source_point to destination_point through the mesh

    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to

    Returns:

        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """

    def find_box(point):
        return next((box for box in mesh["boxes"] if point[0] >= box[0] and point[0] < box[1] and point[1] >= box[2] and point[1] < box[3]), None)
    start = find_box(source_point)
    end = find_box(destination_point)
    if not start or not end:
        print("No path!")
        return [], []
    if start == end:
        return [(source_point, destination_point)], [start]

    grid = {}

    def Node(bounds, h=0, g=inf, f=inf, prev=None, head=True):
        grid[bounds] = {"h": h, "g": g, "f": f, "prev": prev, "head": head}
        return bounds

    def centre(b):
        return ((b[0]+b[1])/2, (b[2]+b[3])/2)

    def dist(a, b):
        return (lambda c, d: ((d[0]-c[0])**2+(d[1]-c[1])**2)**.5)(centre(a), centre(b))

    def tuplify(boxes):
        def clamp(a, b):
            def c(i):
                return max(min(max(a[i], b[i]), centre(a)[i]), min(a[i+1], b[i+1]))
            return (c(0), c(1))
        centres = [destination_point] + (lambda B: [clamp(b, B[i+1])
                                                    for i, b in enumerate(B[:-1])])(boxes[1:-1]) + [source_point]
        return zip(centres[1:], centres[:-1])

    Node(start, g=0)
    Node(end, head=False)

    open_set = [start]
    path = []

    while open_set:
        # get node with min f
        current = min(open_set, key=lambda n: grid[n]["f"])
        if(current == end):  # if at goal
            back = current
            while back:
                path.append(back)
                back = grid[back]["prev"]
            return tuplify(path), grid.keys()

        open_set.remove(current)
        heapify(open_set)
        for neighbour in mesh["adj"][current]:  # check each neighbour
            temp_g = grid[current]["g"] + dist(current, neighbour)
            # check predicted dist
            if neighbour not in grid.keys() or temp_g < grid[neighbour]["g"]:
                Node(neighbour, g=temp_g, f=temp_g +
                     dist(neighbour, end if grid[current]["head"] else start), prev=current, head=grid[current]["head"])
                if neighbour not in open_set:
                    heappush(open_set, neighbour)
    print("No path!")

    return [], grid.keys()
