from planet_wars import issue_order
import sys
sys.path.insert(0, '../')


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(
        state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(),
                         key=lambda t: t.num_ships, default=None)

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
    strongest_planet = max(
        state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(),
                         key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def finishing_attack():  # tries to end game
    pass


def trading_down():  # stalls and trades ships
    pass


def desperado():  # losing planet sends allout attack before dying
    pass


def tacking():  # diversion to target distant target
    pass


def aggressive():  # attack enemy
    # save outputs if we need to optimise
    return attack_weakest_enemy_planet(state) or spread_to_weakest_neutral_planet(state)


def greedy(state):  # attack neutrals
    # save outputs if we need to optimise
    return spread_to_weakest_neutral_planet(state) or attack_weakest_enemy_planet(state)


def defensive():  # protects allies
    pass
