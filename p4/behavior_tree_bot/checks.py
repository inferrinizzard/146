

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
        + sum(fleet.num_ships for fleet in state.my_fleets()) \
        > sum(planet.num_ships for planet in state.enemy_planets()) \
        + sum(fleet.num_ships for fleet in state.enemy_fleets())


def enemy_attack(state):
    return any(fleet for fleet in state.enemy_fleets() if fleet.destination_planet.owner == 1)


def apex(state):
    return max(state.planets, key=lambda p: p.num_ships).owner == 1


def not_apex(state):
    not apex(state)
