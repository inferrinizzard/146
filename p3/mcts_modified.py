from timeit import default_timer as time
from mcts_node import MCTSNode as Node
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_factor = sqrt(2)


def traverse_nodes(node, board, state, identity):  # Node, Board, State, player → Node
    """ Traverses the tree until the end criterion are met.
    Args:
                                                                    node:       A tree node from which the search is traversing.
                                                                    board:      The game setup.
                                                                    state:      The state of the game.
                                                                    identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.
    """

    def UCT(node):  # the one formula
        return node and node.wins / (node.visits or 1) + explore_factor * sqrt(log(node.parent and node.parent.visits or 1)/(node.visits or 1)) or 0

    p1 = identity == 1  # check if p1
    leaf = node
    while leaf.untried_actions and leaf.child_nodes:
        child = (max if p1 else min)(  # find minimax node with UCT
            leaf.child_nodes.values(), key=lambda l: UCT(l))
        p1 = not p1
        leaf = child
        state = board.next_state(state, child.parent_action)  # navigate board
    return leaf


def expand_leaf(node, board, state):  # Node, Board, State → Node
    """ Adds a new leaf to the tree by creating a new child node for the given node.
    Args:
                                                                    node:   The node for which a child will be added.
                                                                    board:  The game setup.
                                                                    state:  The state of the game.

    Returns:    The added child node.
    """

    action = choice(node.untried_actions)  # random action
    node.untried_actions.remove(action)  # pop
    state = board.next_state(state, action)  # navigate board
    leaf = Node(node, action, board.legal_actions(state))  # new node
    node.child_nodes[action] = leaf  # parent pointer

    return leaf


def rollout(board, state):  # Board, State → {1:(-1|1), 2:(-1|1)}
    """ Given the state of the game, the rollout plays out the remainder randomly.
    Args:
                                                                    board:  The game setup.
                                                                    state:  The state of the game.
    """

    ROLLOUTS = 5
    MAX_DEPTH = 3
    # Define a helper function to calculate the difference between the bot's score and the opponent's.

    def outcome(owned_boxes, game_points):
        if game_points is not None:
            # Try to normalize it up?  Not so sure about this code anyhow.
            red_score = game_points[1]*9
            blue_score = game_points[2]*9
        else:
            red_score = len(
                [v for v in owned_boxes.values() if v == 1])
            blue_score = len(
                [v for v in owned_boxes.values() if v == 2])
        return red_score - blue_score if board.current_player(state) == 1 else blue_score - red_score
    while not board.is_ended(state):
        moves = board.legal_actions(state)

        best_move = moves[0]
        best_expectation = float('-inf')

        for move in moves:
            total_score = 0.0

            start = time()
        # Sample a set number of games where the target move is immediately applied.
        for r in range(ROLLOUTS):
            rollout_state = board.next_state(state, move)

            # Only play to the specified depth.
            for i in range(MAX_DEPTH):
                if board.is_ended(rollout_state):
                    break
                rollout_state = board.next_state(
                    rollout_state, choice(board.legal_actions(rollout_state)))
            total_score += outcome(board.owned_boxes(rollout_state),
                                   board.points_values(rollout_state))
            if(time()-start > 1):
                break

        expectation = float(total_score) / ROLLOUTS

        # If the current move has a better average score, replace best_move and best_expectation
        if expectation > best_expectation:
            best_expectation, best_move = expectation, move

        state = board.next_state(state, best_move)
    return board.points_values(state)


def backpropagate(node, won):  # Node, int(0|1) → void
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.
    Args:
                                                                    node:   A leaf node.
                                                                    won:    An indicator of whether the bot won or lost the game.
    """

    while node:
        node.visits = node.visits + 1  # increment visits
        node.wins = node.wins + won  # add won if won
        node = node.parent


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.
    Args:
                                                                    board:  The game setup.
                                                                    state:  The state of the game.

    Returns:    The action to be taken.
    """

    identity_of_bot = board.current_player(state)
    root_node = Node(parent=None, parent_action=None,
                     action_list=board.legal_actions(state))

    tree_size = 100
    num_games = 10
    for step in range(num_games):
        if(tree_size >= num_nodes):
            break
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Selection - Moving down the tree
        node = traverse_nodes(node, board, sampled_game, identity_of_bot)
        if node.parent_action:
            sampled_game = board.next_state(sampled_game, node.parent_action)

        # Expansion - Add new child nodes to the last node we landed on & move there
        if node.untried_actions:
            node = expand_leaf(node, board, sampled_game)
            tree_size = tree_size + 1
            node = traverse_nodes(node, board, sampled_game, identity_of_bot)

        # Simulation - Choose moves until result or predefined state is achieved aka rando time
        point = rollout(board, sampled_game)

        win = point[1] == 1

        # Update value back to the starting point
        backpropagate(node, win)

    # Compare actions ---------
    final = max(root_node.child_nodes.values(),
                key=lambda child: child.wins/child.visits).parent_action

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return final
