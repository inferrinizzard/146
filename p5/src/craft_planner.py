from math import inf
import json
from heapq import heappush, heappop
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time


class Recipe():
    def __init__(self, raw_recipe, complexity=0):
        self.name = list(raw_recipe.keys())[0]
        val = list(raw_recipe.values())[0]
        self.produces = val["Produces"]
        self.time = val["Time"]
        self.requires = list(val.get(
            "Requires").keys()) if val.get("Requires") else []
        self.consumes = val.get("Consumes")
        self.check = make_checker(val)
        self.effect = make_effector(val)
        self.complexity = complexity
        self.raw = raw_recipe
        self.cost = sum(self.consumes.values()) if self.consumes else 0
        # add ten if need tool (maybe adjust this or balance it out against time)
        # self.cost = self.raw_cost + 10 *
        # len(self.requires) if self.requires else 0

    def __repr__(self):  # fancy to_string
        return "<" + self.name + "> Makes " + str(self.produces) + " in " + str(self.time) + " time; "
        + ("Needs: " + str(self.consumes) + "; " if self.consumes else "") + ("Tools: " + ", ".join(self.requires) +
                                                                              " " if self.requires else "") + "Raw Cost: " + str(self.raw_cost) + " Cost: " + str(self.cost) + " Complexity: " + str(self.complexity)

    def __lt__(self, other):
        return self.cost < other.cost


def get_children(item):
    recipes = []
    for key, val in raw.items():
        # get all recipes that need •item
        if(val.get("Consumes") and val["Consumes"].get(item) or val.get("Requires") and val["Requires"].get(item)):
            recipes.append({key: val})
    return recipes


def get_key(d):  # returns key bc python dumb_
    return list(d.keys())[0]


def get_val(d):  # returns val bc python dumb_
    return list(d.values())[0]


# recursively adds all recipes, needs recipes and raw declared outside (recipes:final list, raw:beginning list)
def add_recipes(item, layer=0):
    # print(item, layer)
    if(layer > 5 or len(recipes) == len(raw)):
        return
    makes_item = [{i[0]:i[1]} for i in filter(lambda x: item in list(
        x[1]["Produces"].keys()), raw.items())]  # find recipes that make •item

    # for all recipes related to •item
    for i in [*makes_item, *get_children(item)]:
        name = get_key(i)
        # print("Name: " + name)
        requirements = (lambda req, con: [*(list(req.keys()) if req else []), *(list(con.keys()) if con else [])])(
            get_val(i).get("Requires"), get_val(i).get("Consumes"))  # any item that current •item needs as prereq
        # print(requirements)
        recipe_items = [r for l in [
            list(recipe.produces.keys()) for recipe in recipes] for r in l]

        # check if not dupe and every prereq is satisfied
        if(not any(recipe.name == name for recipe in recipes) and all(req in recipe_items for req in requirements)):
            # print("Added: " + name)

            # make new Recipe if new
            recipes.append(
                Recipe({name: dict(**list(i.values())[0], **{"Complexity": layer})}, layer))
        if(i not in makes_item):  # recurse children
            add_recipes(get_key(get_val(i)["Produces"]), layer+1)
        if((lambda val: not val.get("Requires") and not val.get("Consumes"))(get_val(i))):
            layer += 1


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

    def __repr__(self):
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
        # wow epic in function functions.

        # basicaly if Rules and Consume are in rule then check if stuff is in there.
        if requires:
            for items in requires:
                if state[items] < 1:
                    return False
        if consumes:
            for items, amount in consumes:
                if state[items] < amount:
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
            if not next_state.get(items):
                next_state[items] = 0
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

    return [(r, r.effect(state)) for r in recipes if r.check(state)]


def heuristic(state, recipe):
    # Implement your heuristic here!
    item = list(recipe.produces.keys())[0]
    required = 0
    uses = 0

    if (max_needed.get(item) is None):
        cur_max = 0
        if(item in list(Crafting["Goal"].keys())):
            max_needed[item] = Crafting["Goal"][item]
        else:
            for r in recipes:
                if(r.consumes and r.consumes.get(item) and r.consumes.get(item) > cur_max):
                    cur_max = r.consumes.get(item)
                elif(r.requires and item in r.requires):
                    cur_max = -1
                elif(r.produces.get(item) and r.produces.get(item) > cur_max):
                    cur_max = r.produces.get(item)
        max_needed[item] = cur_max

    if(max_needed[item] < 0 and state[item] == 0):
        return -9000
    if(recipe.requires):
        required = -5
    if(state[item] > 1.5 * max_needed[item]):
        return 9000

    for r in recipes:
        if r.consumes:
            uses += len([_r for _r in r.consumes.keys() if _r == item])
    return -recipe.complexity + recipe.time + required - uses*1.5


def search(graph, state, is_goal, limit, heuristic):
    start_time = time()
    goal = State({key: 0 for key in Crafting['Items']})
    goal.update(Crafting['Goal'])
    game_time = 0

    Queue = [(0, state)]
    prev = {state: None}
    cost = {state: 0}
    action = {state: None}

    while time() - start_time < limit and Queue:
        current_cost, current_state = heappop(Queue)
        # print()
        # print(current_state)
        pending_state = current_state

        if is_goal(current_state):
            path = [(current_state, action[current_state])]
            prev_state = prev[current_state]
            while prev_state:
                path.append((prev_state, action[prev_state]))
                prev_state = prev[prev_state]
            return path

        # print(graph(current_state))
        for next_recipe, next_state in graph(current_state):
            priority = heuristic(current_state.copy(), next_recipe)
            new_cost = cost[current_state] + priority
            # print((next_recipe, priority, new_cost))
            if next_recipe.name not in cost or new_cost < cost[next_state]:
                cost[next_state] = new_cost
                pending_state = next_state
                action[next_state] = next_recipe
                prev[next_state] = current_state.copy()
                heappush(Queue, (priority, next_state))
        current_state = pending_state
        # print(action[current_state])
        # print()

        # Failed to find a path
    # print(Queue)
    # print(prev)
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", current_state, 'within time limit.')
    return None


if __name__ == '__main__':
    with open('crafting.json') as f:
        Crafting = json.load(f)

    # Build rules
    raw = Crafting["Recipes"]
    recipes = []
    add_recipes("wood")

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    max_needed = {}

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t', state)
            print(action)
