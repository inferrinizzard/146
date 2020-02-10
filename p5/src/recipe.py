class Recipe():
    def __init__(self, raw_recipe, complexity=0):
        self.name = list(raw_recipe.keys())[0]
        val = list(raw_recipe.values())[0]
        self.produces = val["Produces"]
        self.time = val["Time"]
        self.requires = val.get("Requires")
        self.consumes = val.get("Consumes")
        self.complexity = complexity
        self.raw = raw_recipe
        self.raw_cost = sum(self.consumes.values()) if self.consumes else 0
        self.cost = self.raw_cost + 10 * \
            len(self.requires) if self.requires else 0  # add ten if need tool (maybe adjust this or balance it out against time)

    def __repr__(self):  # fancy to_string
        return "<" + self.name + "> Makes " + str(self.produces) + " in " + str(self.time) + " time; "
        + ("Needs: " + str(self.consumes) + "; " if self.consumes else "") + ("Tools: " + ", ".join(self.requires.keys()) +
                                                                              " " if self.requires else "") + "Raw Cost: " + str(self.raw_cost) + " Cost: " + str(self.cost) + " Complexity: " + str(self.complexity)


'''↓ all references to crap = Crafting["Recipes"] (aka loaded json from the file)'''


def get_children(item):
    recipes = []
    for key, val in crap.items():
        # get all recipes that need •item
        if(val.get("Consumes") and val["Consumes"].get(item) or val.get("Requires") and val["Requires"].get(item)):
            recipes.append({key: val})
    return recipes


recipes = []


def get_key(d):  # returns key bc python dumb_
    return list(d.keys())[0]


def get_val(d):  # returns val bc python dumb_
    return list(d.values())[0]


# recursively adds all recipes, needs recipes and crap declared outside (recipes:final list, crap:beginning list)
def add_recipes(item, layer=0):
    # print(item, layer)
    if(layer > 5):
        return
    makes_item = [{i[0]:i[1]} for i in filter(lambda x: item in list(
        x[1]["Produces"].keys()), r.items())]  # find recipes that make •item

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


add_recipes("wood")

print(recipes)
