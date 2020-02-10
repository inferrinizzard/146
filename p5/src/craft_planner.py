import json
from math import inf
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from sys import argv

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
                                which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
                                for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
                                default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
                                all items with quantity 0.

                                Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = None
        return next_state

    return effect


def make_goal_checker(goal):
    print(goal.keys())
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        print(state)
        # checks if all items in goal are satisfied in state
        return all(state[item] >= amount for item, amount in goal.items())
        # state[goal]

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state):
    # Implement your heuristic here!

    # recursive check prereqs?
    return 0


def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit:
        pass

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None


if __name__ == '__main__':

    for arg in argv[1:]:
        print(arg)
    with open('Crafting.json') as f:
        Crafting = json.load(f)
        # print(Crafting)

    '''
    preprocess recipes to have total cost / game time / complexity baked
    '''

    # # List of items that can be in your inventory:
    print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    print('Goal:', Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    print('Example recipe:', 'craft stone_pickaxe at bench ->',
          Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 5, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t', state)
            print(action)


# grid = {}

class Recipe():
    def __init__(name, produces, time=1, requires={}, consumes={}):
        self.name = name
        self.produces = produces
        self.time = time
        self.requires = requires
        self.consumes = consumes
        self.complexity =
        self.raw_cost = sum(consumes.values())
        # self.cost = self.raw_cost + sum(requires.values())

# class Node():
#     def __init__(h=0, g=inf, prev=None):
#         self.h = h
#         self.g = g
#         self.f = h + g
#         self.prev = None

# end = Node()
# open_set = [Node(start, g=0)]
# path = []

# while open_set:
# 		# get node with min f
# 		current = min(open_set, key=lambda n: grid[n]["f"])
# 		if(current == end):  # if at goal
# 				back = current
# 				while back:
# 						path.append(back)
# 						back = grid[back]["prev"]
# 				return tuplify(path), grid.keys()

# 		open_set.remove(current)
# 		heapify(open_set)
# 		for neighbour in mesh["adj"][current]:  # check each neighbour
# 				temp_g = grid[current]["g"] + dist(current, neighbour)
# 				# check predicted dist
# 				if neighbour not in grid.keys() or temp_g < grid[neighbour]["g"]:
# 						Node(neighbour, g=temp_g, f=temp_g +
# 									dist(neighbour, end if grid[current]["head"] else start), prev=current, head=grid[current]["head"])
# 						if neighbour not in open_set:
# 								heappush(open_set, neighbour)
