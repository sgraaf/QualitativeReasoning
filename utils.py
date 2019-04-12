from itertools import product

import pygraphviz as pgv

def generate_states():
    """
    Generate a list of possible states (= permutations of quantity spaces).

    :returns: list of possible states
    """
    derivative = ['-', '0', '+']
    inflow = ['0', '+']
    volume = outflow = ['0', '+', 'max']
    return list(product(*[inflow, derivative, volume, derivative, outflow, derivative]))


def sort_states(states):
    """
    Sort a list of states in-place, based on their values.

    :param states: a list of states
    """
    sort_order = {'-': 0, '0': 1, '+': 2, 'max': 3}
    
    for i in range(len(states[0]) - 1, -1, -1):
        states.sort(key=lambda x: sort_order[x[i]])


def is_valid_state(state, debug_states):
    """
    Determine if a given state is valid or not, given the dependencies and assumptions.

    :param state: a possible state
    :param debug_states: list of states to debug
    :returns: true if valid, false otherwise
    """

    debug = False
    if state in debug_states:
        debug = True

    # validate the state, based on the given dependencies
    # I+(Inflow, Volume)
    if state[0] == '+':  # positive inflow
        if state[3] != '+':  # no positive volume gradient
            if state[4] == '0':  # 0 outflow
                if debug:
                    print(f'Invalid state (I+(Inflow, Volume)): {state}')
                return False
    elif state[0] == '0':  # 0 inflow
        if state[3] == '+':  # positive volume gradient
            if debug:
                print(f'Invalid state (I+(Inflow, Volume)): {state}')
            return False

    # I-(Outflow, Volume)
    if state[4] == 'max':  # max outflow
        if state[3] != '-':  # no negative volume gradient
            if debug:
                print(f'Invalid state (I-(Outflow, Volume)): {state}')
            return False
    elif state[4] == '+':  # positive outflow
        if state[3] != '-':  # no negative volume gradient
            if state[0] == '0':  # 0 inflow
                if debug:
                    print(f'Invalid state (I-(Outflow, Volume)): {state}')
                return False
    elif state[4] == '0':  # 0 outflow
        if state[3] != '0':  # no positive volume gradient
            if state[0] == '0':  # 0 inflow
                if debug:
                    print(f'Invalid state (I-(Outflow, Volume)): {state}')
                return False

    # P+(Volume, Outflow)
    if state[3] != state[5]:  # inequal volume and outflow gradients
        if debug:
            print(f'False on P+(Volume, Outflow) 1: {state}')
        return False

    # VC(Volume(max), Outflow(max))
    if state[2] == 'max':  # max volume
        if state[4] != 'max':  # no max outflow
            if debug:
                print(f'Invalid state (VC(Volume(max), Outflow(max))): {state}')
            return False
    elif state[2] != 'max':  # no max volume
        if state[4] == 'max':  # max outflow
            if debug:
                print(f'Invalid state (VC(Volume(max), Outflow(max))): {state}')
            return False

    # VC(Volume(0), Outflow(0))
    if state[2] == '0':  # 0 volume
        if state[4] != '0':  # no 0 outflow
            if debug:
                print(f'Invalid state (VC(Volume(0), Outflow(0))): {state}')
            return False
    # elif state[2] != '0':  # no 0 volume
    #     if state[4] == '0':  # 0 outflow
    #         if debug:
    #             print(f'Invalid state (VC(Volume(0), Outflow(0))): {state}')
    #         return False

    # validate the state, based on assumptions
    # assumption: inflow can't increase when it's "max" nor decrease when it's 0
    if state[0] == '+':  # "max" inflow
        if state[1] == '+':  # positive inflow gradient
            if debug:
                print(f'Invalid state (assumption that inflow can\'t increase when it\'s "max"): {state}')
            return False
    elif state[0] == '0':  # 0 inflow
        if state[1] == '-':  # negative inflow gradient
            if debug:
                print(f'Invalid state (assumption that inflow can\'t decrese when it\'s 0): {state}')
            return False

    # assumption: volume can't increase when it's max nor decrease when it's 0
    if state[2] == 'max':  # max volume
        if state[3] == '+':  # positive volume gradient
            if debug:
                print(f'Invalid state (assumption that volume can\'t increase when it\'s max): {state}')
            return False
    elif state[2] == '0':  # 0 volume
        if state[3] == '-':  # negative volume gradient
            if debug:
                print(f'Invalid state (assumption that volume can\'t decrese when it\'s 0): {state}')
            return False

    # assumption: outflow can't increase when it's max nor decrease when it's 0
    if state[4] == 'max':  # max outflow
        if state[5] == '+':  # positive outflow gradient
            if debug:
                print(f'Invalid state (assumption that outflow can\'t increase when it\'s max): {state}')
            return False
    elif state[4] == '0':  # 0 outflow
        if state[5] == '-':  # negative outflow gradient
            if debug:
                print(f'Invalid state (assumption that outflow can\'t decrese when it\'s 0): {state}')
            return False

    return True


def id_states(states):
    """
    Give the states an numeric ID.

    :param states: a list of states
    :returns: a list of states, with numeric IDs at the last index
    """
    id_states = []
    for i in range(len(states)):
        id_states.append(states[i] + (i + 1,))
    return id_states


def is_valid_transition(state_transition, debug_state_transitions):
    """
    Determine if a given state transition is valid or not, given the dependencies and assumptions.

    :param state_transition: a possible state transition
    :returns: true if valid, false otherwise
    """
    state_1, state_2 = state_transition

    debug = False
    if state_transition in debug_state_transitions:
        debug = True

    # (in)validate the magnitudes of state_2, based on the magnitudes and gradients of state_1    
    # 1: no magnitude change possible if gradient is 0
    if state_1[1] == '0':  # 0 inflow gradient state_1
        if state_1[0] != state_2[0]:  # inequal inflows state_1-state_2
            if debug:
                print(f'Invalid state transition (0 inflow gradient): {state_1} --> {state_2}')
            return False
    
    if state_1[3] == '0':  # 0 volume gradient state_1
        if state_1[2] != state_2[2]:  # inequal volumes state_1-state_2
            if debug:
                print(f'Invalid state transition (0 volume gradient): {state_1} --> {state_2}')
            return False
    
    if state_1[5] == '0':  # 0 outflow gradient state_1
        if state_1[4] != state_2[4]:  # inequal outflows state_1-state_2
            if debug:
                print(f'Invalid state transition (0 outflow gradient): {state_1} --> {state_2}')
            return False

    # 2: no magnitude change possible from 0 to max and vice-versa
    if state_1[2] == '0' and state_2[2] == 'max':  # 0 volume state_1 and max volume state_2
        if debug:
            print(f'Invalid state transition (0-to-max volume): {state_1} --> {state_2}')
        return False
    elif state_1[2] == 'max' and state_2[2] == '0':  # max volume state_1 and 0 volume state_2
        if debug:
            print(f'Invalid state transition (max-to-0 volume): {state_1} --> {state_2}')
        return False

    if state_1[4] == '0' and state_2[4] == 'max':  # 0 outflow state_1 and max outflow state_2
        if debug:
            print(f'Invalid state transition (0-to-max outflow): {state_1} --> {state_2}')
        return False
    elif state_1[4] == 'max' and state_2[4] == '0':  # max outflow state_1 and 0 outflow state_2
        if debug:
            print(f'Invalid state transition (max-to-0 outflow): {state_1} --> {state_2}')
        return False
    
    # 3: no magnitude change possible from 0 to + and + to max if gradient is -
    if state_1[1] == '-':  # negative inflow gradient
        if state_1[0] == '0' and state_2[0] == '+':  # 0-to-pos inflow increase
            if debug:
                print(f'Invalid state transition (0-to-pos inflow with negative gradient): {state_1} --> {state_2}')
            return False
    
    if state_1[3] == '-':  # negative volume gradient
        if state_1[2] == '0' and state_2[2] == '+':  # 0-to-pos volume increase
            if debug:
                print(f'Invalid state transition (0-to-pos volume with negative gradient): {state_1} --> {state_2}')
            return False
        elif state_1[2] == '+' and state_2[2] == 'max':  # pos-to-max volume increase
            if debug:
                print(f'Invalid state transition (pos-to-max volume with negative gradient): {state_1} --> {state_2}')
            return False

    if state_1[5] == '-':  # negative outflow gradient
        if state_1[4] == '0' and state_2[4] == '+':  # 0-to-pos outflow increase
            if debug:
                print(f'Invalid state transition (0-to-pos outflow with negative gradient): {state_1} --> {state_2}')
            return False
        elif state_1[4] == '+' and state_2[4] == 'max':  # pos-to-max outflow increase
            if debug:
                print(f'Invalid state transition (pos-to-max outflow with negative gradient): {state_1} --> {state_2}')
            return False

    # 4: no magnitude change possible from + to 0 and max to + if gradient is +
    if state_1[1] == '+':  # positive inflow gradient
        if state_1[0] == '+' and state_2[0] == '0':  # pos-to-0 inflow increase
            if debug:
                print(f'Invalid state transition (pos-to-0 inflow with positive gradient): {state_1} --> {state_2}')
            return False
    
    if state_1[3] == '+':  # positive volume gradient
        if state_1[2] == '+' and state_2[2] == '0':  # pos-to-0 volume increase
            if debug:
                print(f'Invalid state transition (pos-to-0 volume with positive gradient): {state_1} --> {state_2}')
            return False
        elif state_1[2] == 'max' and state_2[2] == '+':  # max-to-pos volume increase
            if debug:
                print(f'Invalid state transition (max-to-pos volume with positive gradient): {state_1} --> {state_2}')
            return False

    if state_1[5] == '+':  # positive outflow gradient
        if state_1[4] == '+' and state_2[4] == '0':  # pos-to-0 outflow increase
            if debug:
                print(f'Invalid state transition (pos-to-0 outflow with positive gradient): {state_1} --> {state_2}')
            return False
        elif state_1[4] == 'max' and state_2[4] == '+':  # max-to-pos outflow increase
            if debug:
                print(f'Invalid state transition (max-to-pos outflow with positive gradient): {state_1} --> {state_2}')
            return False
   
    # 5: point-magnitudes can't remain the same if the gradient is non-zero
    if state_1[0] != '+' and state_1[0] == state_2[0] and state_1[1] != '0':
        if debug:
            print(f'Invalid state transition (same point-magnitudes with non-zero gradient for inflow): {state_1} --> {state_2}')
        return False
    elif state_1[2] != '+' and state_1[2] == state_2[2] and state_1[3] != '0':
        if debug:
            print(f'Invalid state transition (same point-magnitudes with non-zero gradient for volume): {state_1} --> {state_2}')
        return False
    elif state_1[4] != '+' and state_1[4] == state_2[4] and state_1[5] != '0':
        if debug:
            print(f'Invalid state transition (same point-magnitudes with non-zero gradient for outflow): {state_1} --> {state_2}')
        return False

    # 6: no gradient changes possible from neg-to-pos and pos-to-neg
    if state_1[1] == '-' and state_2[1] == '+':
        if debug:
            print(f'Invalid state transition (neg-to-pos gradient change for inflow): {state_1} --> {state_2}')
        return False
    elif state_1[1] == '+' and state_2[1] == '-':
        if debug:
            print(f'Invalid state transition (pos-to-neg gradient change for inflow): {state_1} --> {state_2}')
        return False

    if state_1[3] == '-' and state_2[3] == '+':
        if debug:
            print(f'Invalid state transition (neg-to-pos gradient change for volume): {state_1} --> {state_2}')
        return False
    elif state_1[3] == '+' and state_2[3] == '-':
        if debug:
            print(f'Invalid state transition (pos-to-neg gradient change for volume): {state_1} --> {state_2}')
        return False

    if state_1[5] == '-' and state_2[5] == '+':
        if debug:
            print(f'Invalid state transition (neg-to-pos gradient change for outflow): {state_1} --> {state_2}')
        return False
    elif state_1[5] == '+' and state_2[5] == '-':
        if debug:
            print(f'Invalid state transition (pos-to-neg gradient change for outflow): {state_1} --> {state_2}')
        return False
    
    return True


def get_state_representation(state):
    """
    Get the representation of the state in human-readable form.

    :param state: the state
    :returns: the representation of the state
    """
    return f'State {state[6]}\nInflow: [{state[0]}, {state[1]}]\nVolume: [{state[2]}, {state[3]}]\nOutflow: [{state[4]}, {state[5]}]'


def trace(state_transition):
    """
    Get the inter-state trace of a state-transition.

    :param state_transition: the state-transition
    :returns: the inter-state trace of the state-transition
    """
    state_1, state_2 = state_transition

    out_str = ''

    # erratic behaviour of the tap and its rammifications
    if state_1[0] == state_2[0] and state_1[1] != state_2[1]:
        out_str += 'E+'
    elif state_1[2] == state_2[2] and state_1[3] != state_2[3]:
        if state_1[0] == state_2[0] and state_1[4] == state_2[4]:
            out_str += 'E+'
    elif state_1[4] == state_2[4] and state_1[5] != state_2[5]:
        if state_2[3] != state_2[5]:
            out_str += 'E+'
    
    # interval
    if (state_1[2:6] == state_2[2:6]):
        out_str += 'I+'

    # magnitude change due to derivative
    if state_1[0] != state_2[0]:
        out_str += 'D+'
    elif state_1[2] != state_2[2]:
        out_str += 'D+'
    elif state_1[4] != state_2[4]:
        out_str += 'D+'
    
    return out_str[:-1]


def create_state_transition_graph(states, state_transitions):
    """
    Create the state-transition graph, given the states and state-transitions.

    :param states: list of valid states of the qualitative model
    :param state_transitions: list of valid state-transitions of the qualitative model
    """
    graph = pgv.AGraph(
        directed=True, 
        overlap=False, 
        splines=True, 
        sep=+0.5, 
        normalize=True, 
        smoothing='avg_dist')
    
    for state_transition in state_transitions:
        state_1, state_2 = state_transition
        representation_1 = get_state_representation(state_1)
        representation_2 = get_state_representation(state_2)
        trace_label = trace(state_transition)
        graph.add_edge(representation_1, representation_2, label=trace_label)

    graph.write('./Output/graph.dot')
    graph.draw('./Output/graph.svg', prog='dot')
    graph.draw('./Output/graph.png', prog='dot')

    # remove any inconsequential states
    for node in graph.nodes():
        in_edges = list(graph.iterinedges(node))

        if len(in_edges) == 0:  # no incoming edges, so never reached
            graph.remove_node(node)

    graph.write('./Output/graph_2.dot')
    graph.draw('./Output/graph_2.svg', prog='dot')
    graph.draw('./Output/graph_2.png', prog='dot')