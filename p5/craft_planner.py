import json
#import recipe
from heapq import heappush, heappop
import math
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time


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
    requires = None
    consumes = None
    if 'Requires' in rule:
        requires = rule['Requires']
    if 'Consumes' in rule:
        consumes = rule['Consumes'].items()

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        #wow epic in function functions.

        #basicaly if Rules and Consume are in rule then check if stuff is in there.
        if consumes:
            for items, amount in consumes:
                if state[items] < amount:
                    return False
        
        if requires:
            for items in requires:
                if state[items] < 1:
                    return False

        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    consumes = None
    produces = rule['Produces'].items()

    if 'Consumes' in rule:
        consumes = rule['Consumes'].items()

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()

        if consumes:
            for items, amount in consumes:
                next_state[items] -= amount
        
        for items, amount in produces:
            next_state[items] += amount


        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    goal_items = goal.items()

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for items, amount in goal_items:
            if state[items] < amount:
                return False
        return True

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
    #makes = Crafting['Produces'].items()
    # state returns items
    #tool id's are bench, furnace, iron_axe, iron_pickaxe, stone_axe, stone_pickaxe, wooden_axe, wooden_pickaxe
    tools = ["bench","furnace","iron_axe","iron_pickaxe","stone_axe","stone_pickaxe","wooden_axe","wooden_pickaxe"]

    for tool in tools:
        if tool in state:
            return 9000 #funny meme number for tool heuristic its 2 am and im losing it. using inf just breaks program

    # I've noticed the program sometimes mines like 3million coal for literally no reason
    #maybe its a good idea to put limits on some stuff.
    
    items = {"plank": 4, "stick": 4, "coal": 1, "cobble": 8, "ore": 1, "wood": 1, "ingot": 6}
    for item, count in items:
        if item in state:
            if state[item] > count:
                return 9000
    



    return 0
    """
    for r in all_recipes:
        makes = r['Produces'].items()
        need_tool = not state[makes[0]]
        required = 0
        uses = 0
        if need_tool and any(_r in r.requires for _r in makes):
            required = -2  # prioritise tools if not yet made

        if r.consumes:
            for item in [_r for _r in r.consumes.keys() for _r in makes]:
                #uses += 1/(state[item]+1) # tries to prevent hoarding but doesn't work>
                uses += 1  # will get stuck at stone_axe
    return -all_recipes.complexity + required - uses
    # lower number → higher priority | delete the last two when done 
    """

"""
def search(graph, state, is_goal, limit, heuristic):

    start_time = time()
    goal = State({key: 0 for key in Crafting['Items']})
    goal.update(Crafting['Goal'])

    print(goal)

    Queue = []
    prev = {}
    cost = {}
    prev[goal] = None
    cost[goal] = 0

    path = {}
    path[goal] = None
    is_state = state.copy()
    heappush(Queue, (0, goal))

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit and Queue:
        curr_cost, current = heappop(Queue)

        if current == state:
            #then we're done 
            print(path)
            path_tuple = [(current, path[current])]

            prev_pointer = prev[current]
            # most of this is similar to the past assignments A* path return
            while prev_pointer is not None:
                path_tuple.insert(0, (prev_pointer, path[prev_pointer]))
                prev_pointer = prev[prev_pointer]
            return path_tuple
        neighbors = graph(current)

        for next_name, next_state, next_cost in neighbors:
            print(next_name)
            new_cost = curr_cost + next_cost
            if next_name not in cost or new_cost < cost[next_state]:
                cost[next_state] = new_cost
                priority = new_cost + heuristic(next_state)
                #can't figure out what action is supposed to mean so i'll assume it means name
                path[next_state] = next_name
                heappush(Queue, (priority, next_state))
                prev[next_state] = current


    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", goal, 'within time limit.')
    return None
"""


def search(graph, state, is_goal, limit, heuristic):

    start_time = time()
    Queue = []
    prev = {}
    cost = {}
    prev[state] = None
    cost[state] = 0

    path = {}
    path[state] = None
    heappush(Queue, (0, state))

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit and Queue:
        curr_cost, current = heappop(Queue)

        if is_goal(current):
            #then we're done 
            path_tuple = [(current, path[current])]

            prev_pointer = prev[current]
            # most of this is similar to the past assignments A* path return
            while prev_pointer is not None:
                path_tuple.insert(0, (prev_pointer, path[prev_pointer]))
                prev_pointer = prev[prev_pointer]
            return path_tuple
        neighbors = graph(current)

        for next_name, next_state, next_cost in neighbors:
            #print(cost[current])
            new_cost = curr_cost + next_cost
            if next_name not in cost or new_cost < cost[next_state]:
                cost[next_state] = new_cost
                priority = new_cost + heuristic(next_state)
                #can't figure out what action is supposed to mean so i'll assume it means name
                path[next_state] = next_name
                heappush(Queue, (priority, next_state))
                prev[next_state] = current


    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

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
        total_cost = 0
        for state, action in resulting_plan:
            if action:
                total_cost += Crafting['Recipes'][action]['Time']
            print('\t',state)
            print(action)
        print("[cost=",total_cost,"]")
