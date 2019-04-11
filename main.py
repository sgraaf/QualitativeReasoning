from itertools import product

import pygraphviz as pgv

from utils import *

# Step 1: (Over)generate states
states = generate_states()
states_len = len(states)
print(f'Step 1: (Over)generated {states_len} states in total!')

# Step 1a: Sort the states
sort_states(states)

# Step 2: Remove any invalid states
debug_states = [
    ('0', '0', '0', '0', '0', '0'),
    ('0', '+', '0', '0', '0', '0'),
    ('+', '0', '0', '+', '0', '+'),
]

valid_states = [state for state in states if is_valid_state(state, debug_states)]
valid_states_len = len(valid_states)
print(f'Step 2: Removed {states_len - valid_states_len} invalid states, there are {valid_states_len} valid states remaining')

# Step 3: (Over)generate state-transitions
state_transitions = list(product(valid_states, repeat=2))
transitions_len = len(state_transitions)
print(f'Step 3: (Over)generated {transitions_len} state transitions in total!')

# Step 4: Remove any invalid state-transitions
debug_state_transitions = [
    (('0', '0', '0', '0', '0', '0'), ('0', '+', '0', '0', '0', '0'),),
    (('0', '0', '0', '0', '0', '0'), ('0', '+', '0', '0', '0', '0'),),
    (('0', '+', '0', '0', '0', '0'), ('+', '0', '0', '+', '0', '+'),),
    (('+', '0', '0', '+', '0', '+'), ('+', '0', '+', '+', '+', '+'),),
    (('+', '0', '0', '+', '0', '+'), ('+', '0', '+', '0', '+', '0'),),
    (('+', '0', '+', '+', '+', '+'), ('+', '0', '+', '+', '+', '+'),),
    (('+', '0', '+', '+', '+', '+'), ('+', '-', '+', '+', '+', '+'),),
    (('+', '0', '+', '+', '+', '+'), ('+', '0', 'max', '0', 'max', '0'),),
    (('+', '-', '+', '+', '+', '+'), ('+', '-', '+', '+', '+', '+'),),
    (('+', '-', '+', '+', '+', '+'), ('+', '-', 'max', '0', 'max', '0'),),
    (('+', '0', '0', '+', '0', '+'), ('+', '-', '0', '+', '0', '+'),)
]

valid_state_transitions = [state_transition for state_transition in state_transitions if is_valid_transition(state_transition, debug_state_transitions)]
valid_transitions_len = len(valid_state_transitions)
print(f'Step 4: Removed {transitions_len - valid_transitions_len} invalid states transitions, there are {valid_transitions_len} valid state transitions remaining')

# Step 5: Create graph of the qualitative model using these valid states and state-transitions
create_state_transition_graph(valid_states, valid_state_transitions)
