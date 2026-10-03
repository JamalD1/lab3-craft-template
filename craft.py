import random
from recipes import CAPACITY, RECIPES

def craft(inventory, recipe_name, player_level):
    if type(player_level) is not int or player_level < 1:
        raise ValueError
    recipe = RECIPES.get(recipe_name)
    if not recipe or player_level < recipe["level_req"]:
        raise ValueError

    pool = sorted(inventory, key=lambda x: x.get("quality", 1), reverse=True)
    to_remove = []
    for name, qty in recipe["ingredients"].items():
        found = [x for x in pool if x.get("name") == name]
        if len(found) < qty:
            raise ValueError
        to_remove.extend(found[:qty])

    if len(inventory) - len(to_remove) + 1 > CAPACITY:
        raise ValueError

    if random.random() >= recipe["fail_chance"]:
        for item in to_remove:
            inventory.remove(item)
        res = {"name": recipe["result"], "quality": 5}
        inventory.append(res)
        return res
    else:
        for item in to_remove:
            inventory.remove(item)
        return None
