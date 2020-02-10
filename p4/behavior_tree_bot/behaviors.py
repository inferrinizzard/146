from planet_wars import issue_order
import logging
from sys import path
path.insert(0, '../')


def weakest(planets):
    return min(planets, key=lambda p: p.num_ships, default=None)


def strongest(planets):
    return max(planets, key=lambda p: p.num_ships, default=None)


def closest_ally(planet, state):
    return min(list(filter(lambda x: x != planet, state.my_planets())), key=lambda p: state.distance(planet.ID, p.ID), default=None)


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = strongest(state.my_planets())

    # (3) Find the weakest enemy planet.
    weakest_planet = weakest(state.enemy_planets())

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = strongest(state.my_planets())

    # (3) Find the weakest neutral planet.
    weakest_planet = weakest(state.neutral_planets())

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest(state):
    weakest_planet = weakest(state.my_planets())
    closest_ally = closest(weakest_planet, state)
    return issue_order(state, closest_ally.ID, weakest_planet.ID, closest_ally.num_ships/2)


def protect_weakest_ally(state):
    weakest_ally = weakest(state.my_planets())
    strongest_ally = strongest(state.my_planets())
    return issue_order(state, strongest_ally.ID, weakest_ally.ID, (strongest_ally.num_ships - weakest_ally.num_ships) / 2)


def highest_growth(state):  # prioritise at the start of the game
    best_grower = max(state.neutral_planets(),
                      key=lambda p: p.growth_rate, default=None)
    strongest_ally = strongest(state.my_planets())
    return issue_order(state, strongest_ally.ID, best_grower.ID, strongest_ally.num_ships / 2)


def attack_plan(state):
    my_planets = iter(
        sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    target_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    target_planets = iter(
        sorted(target_planets, key=lambda p: p.num_ships, reverse=True))
    sent_ship = False
    try:
        # my_planet = next(my_planets)
        target_planet = next(target_planets)
        my_planet = closest_ally(target_planet, state)
        while True:
            required_ships = target_planet.num_ships + \
                state.distance(my_planet.ID, target_planet.ID) * \
                target_planet.growth_rate + 1
            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID,
                            target_planet.ID, required_ships)
                sent_ship = True
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                target_planet = next(target_planets)

    except StopIteration:
        return sent_ship


def spread_plan(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets()) and planet.growth_rate > 0]
    neutral_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(neutral_planets)
    sent_ship = False
    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + 1
            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID,
                            target_planet.ID, required_ships)
                sent_ship = True
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return sent_ship


def omega_spread(state):
    own_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)
    if(not state.neutral_planets()):
        return False
    neutral_planets = sorted(state.neutral_planets(),
                             key=lambda p: p.num_ships)
    for planet in own_planets:
        num_cur = planet.num_ships
        num_start = planet.num_ships
        if not neutral_planets:
            break
        target_planet = neutral_planets[-1]
        while num_cur > num_start / 3 + target_planet.num_ships:
            num_cur = num_cur + target_planet.num_ships + 1
            neutral_planets.pop()
            issue_order(state, planet.ID, target_planet.ID,
                        target_planet.num_ships+1)
            if(neutral_planets):
                target_planet = neutral_planets[-1]
            else:
                break
    return True


# Check to see if neutral planets are available. Aggressive/Spread Strategy
def deny_enemy_fleet(state):
    fleets_to_neutral = [fleet for fleet in state.enemy_fleets()
                         if fleet.destination_planet in [planet.ID for planet in state.not_my_planets()]
                         and not any(fleet.destination_planet == my_fleet.destination_planet for my_fleet in state.my_fleets())]

    for fleet in fleets_to_neutral:
        enemy_dest = next(
            filter(lambda p: p.ID == fleet.destination_planet, state.neutral_planets()))
        for planet in state.my_planets():
            travel_turns = state.distance(planet.ID, enemy_dest.ID)
            turns_enemy_owns = travel_turns - fleet.turns_remaining
            if turns_enemy_owns > 0:
                req_ships = (fleet.num_ships - enemy_dest.num_ships) + \
                    turns_enemy_owns * enemy_dest.growth_rate + 1
                if req_ships < planet.num_ships and req_ships > 0:
                    return issue_order(state, planet.ID, enemy_dest.ID, req_ships)

    return False


def do_nothing(state):
    return True


def order_alpha(state):
    apex = strongest(state.my_planets())
    enemies = sorted([planet for planet in state.enemy_planets()
                      if planet.num_ships < apex.num_ships], key=lambda p: p.num_ships)
    if(not enemies):
        return False
    num = apex.num_ships
    threshold = apex.num_ships / 4
    index = 0
    while num > threshold:
        target_planet = enemies[index]
        required_ships = target_planet.num_ships + 1 + \
            state.distance(apex.ID, target_planet.ID) * \
            target_planet.growth_rate + 1
        num = num - required_ships
        issue_order(state, apex.ID,
                    target_planet.ID, required_ships)
    return True
