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
    Sort a list of states, based on their values.

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
                    print(f'False on I+(Inflow, Volume) 1: {state}')
                return False
    elif state[0] == '0':  # 0 inflow
        if state[3] == '+':  # positive volume gradient
            if debug:
                print(f'False on I+(Inflow, Volume) 2: {state}')
            return False

    # I-(Outflow, Volume)
    if state[4] == '+':  # positive outflow
        if state[3] != '-':  # no negative volume gradient
            if state[0] == '0':  # 0 inflow
                if debug:
                    print(f'False on I-(Outflow, Volume) 1: {state}')
                return False
    elif state[4] == '0':  # 0 outflow
        if state[3] != '0':  # no positive volume gradient
            if state[0] == '0':  # 0 inflow
                if debug:
                    print(f'False on I-(Outflow, Volume) 2: {state}')
                return False

    # P+(Volume, Outflow)
    if state[3] == '+':  # positive volume gradient
        if state[5] != '+':  # no positive outflow gradient
            if debug:
                print(f'False on P+(Volume, Outflow) 1: {state}')
            return False
    elif state[3] == '-':  # negative volume gradient
        if state[5] != '-':  # no negative outflow gradient
            if debug:
                print(f'False on P+(Volume, Outflow) 2: {state}')
            return False
    elif state[3] == '0':  # 0 volume gradient
        if state[5] != '0':  # no 0 outflow gradient
            if debug:
                print(f'False on P+(Volume, Outflow) 3: {state}')
            return False

    # VC(Volume(max), Outflow(max))
    if state[2] == 'max':  # max volume
        if state[4] != 'max':  # no max outflow
            if debug:
                print(f'False on VC(Volume(max), Outflow(max)) 1: {state}')
            return False
    elif state[2] != 'max':  # no max volume
        if state[4] == 'max':  # max outflow
            if debug:
                print(f'False on VC(Volume(max), Outflow(max)) 2: {state}')
            return False

    # VC(Volume(0), Outflow(0))
    if state[2] == '0':  # 0 volume
        if state[4] != '0':  # no 0 outflow
            if debug:
                print(f'False on VC(Volume(0), Outflow(0)) 1: {state}')
            return False
    elif state[2] != '0':  # no 0 volume
        if state[4] == '0':  # 0 outflow
            return False

    # validate the state, based on assumptions
    # assumption: inflow can't increase when it's "max" nor decrease when it's 0
    if state[0] == '+':  # "max" inflow
        if state[1] == '+':  # positive inflow gradient
            if debug:
                print(f'''False on assumption: inflow can't increase when it's "max" nor decrease when it's 0: {state}''')
            return False
    if state[0] == '0':  # 0 inflow
        if state[1] == '-':  # negative inflow gradient
            if debug:
                print(f'''False on assumption: inflow can't increase when it's "max" nor decrease when it's 0: {state}''')
            return False

    # assumption: volume can't increase when it's max nor decrease when it's 0
    if state[2] == 'max':  # max volume
        if state[3] == '+':  # positive volume gradient
            if debug:
                print(f'''False on assumption: volume can't increase when it's max nor decrease when it's 0: {state}''')
            return False
    elif state[2] == '0':  # 0 volume
        if state[3] == '-':  # negative volume gradient
            if debug:
                print(f'''False on assumption: volume can't increase when it's max nor decrease when it's 0: {state}''')
            return False

    # assumption: outflow can't increase when it's max nor decrease when it's 0
    if state[4] == 'max':  # max outflow
        if state[5] == '+':  # positive outflow gradient
            if debug:
                print(f'''False on assumption: outflow can't increase when it's max nor decrease when it's 0: {state}''')
            return False
    elif state[4] == '0':  # 0 outflow
        if state[5] == '-':  # negative outflow gradient
            if debug:
                print(f'''False on assumption: outflow can't increase when it's max nor decrease when it's 0: {state}''')
            return False

    return True


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

    # validate the magnitudes of state_2, based on the magnitudes and gradients of state_1
    # gradients of the inflow
    if state_1[1] == '0':  # 0 inflow gradient state_1
        if state_1[0] != state_2[0]:  # inequal inflows state_1-state_2
            if debug:
                print(f'Invalid state transition (0 inflow gradient): {state_1} --> {state_2}')
            return False
    
    # gradients of the volume
    if state_1[3] == '-':  # negative volume gradient state_1
        if state_1[2] == '+':  # positive volume state_1
            if state_2[2] == 'max':  # max volume state_1
                if debug:
                    print(f'Invalid state transition (negative volume gradient, positive volume): {state_1} --> {state_2}')
                return False
        elif state_1[2] == 'max':  # max volume state_1
            if state_2[2] != '+':  # no positive volume state_2
                if debug:
                    print(f'Invalid state transition (negative volume gradient, max volume): {state_1} --> {state_2}')
                return False
    elif state_1[3] == '0':  # 0 volume gradient state_1
        if state_1[2] != state_2[2]:  # inequal volumes state_1-state_2
            if debug:
                print(f'Invalid state transition (0 volume gradient): {state_1} --> {state_2}')
            return False
    elif state_1[3] == '+':  # positive volume gradient state_1
        if state_1[2] == '0':  # 0 volume state_1
            if state_2[2] != '+':  # no positive state_1
                if debug:
                    print(f'Invalid state transition (positive volume gradient, 0 volume): {state_1} --> {state_2}')
                return False
        elif state_1[2] == '+':  # positive volume state_1
            if state_2[2] == '0':  # 0 volume state_2
                if debug:
                    print(f'Invalid state transition (positive volume gradient, positive volume): {state_1} --> {state_2}')
                return False

    # gradients of the outflow
    if state_1[5] == '-':  # negative outflow gradient state_1
        if state_1[4] == '+':  # positive outflow state_1
            if state_2[4] == 'max':  # max outflow state_1
                if debug:
                    print(f'Invalid state transition (negative outflow gradient, positive outflow): {state_1} --> {state_2}')
                return False
        elif state_1[4] == 'max':  # max outflow state_1
            if state_2[4] != '+':  # ni positive outflow state_2
                if debug:
                    print(f'Invalid state transition (negative outflow gradient, max outflow): {state_1} --> {state_2}')
                return False
    elif state_1[5] == '0':  # 0 outflow gradient state_1
        if state_1[4] != state_2[4]:  # inequal outflows state_1-state_2
            if debug:
                    print(f'Invalid state transition (0 outflow gradient): {state_1} --> {state_2}')
            return False
    elif state_1[5] == '+':  # positive outflow gradient state_1
        if state_1[4] == '0':  # 0 outflow state_1
            if state_2[4] != '+':  # no positive outflow state_1
                if debug:
                    print(f'Invalid state transition (positive outflow gradient, 0 outflow): {state_1} --> {state_2}')
                return False
        elif state_1[4] == '+':  # positive outflow state_1
            if state_2[4] == '0':  # 0 outflow state_2
                if debug:
                    print(f'Invalid state transition (positive outflow gradient, positive outflow): {state_1} --> {state_2}')
                return False

    # equal magnitudes
    if state_1[0:-1:2] == state_2[0:-1:2]:
        if state_1[3] != state_2[3]:
            if debug:
                print(f'Invalid state transition (equal magnitudes, different gradients): {state_1} --> {state_2}')
            return False
        elif state_1[5] != state_2[5]:
            if debug:
                print(f'Invalid state transition (equal magnitudes, different gradients): {state_1} --> {state_2}')
            return False

    # validate the state transition, based on the given dependencies
    # I+(Inflow, Volume)
    # if state_1[0] == '+':  # positive inflow state_1
    #     if state_1[4] == '0':  # 0 outflow state_1
    #         if state_2[3] != '+':  # no positive volume gradient state_2
    #             if debug:
    #                 print(f'Invalid state transition (I+(Inflow, Volume), positive inflow): {state_1} --> {state_2}')
    #             return False
    # elif state_1[0] == '0':  # 0 inflow state_1
    #     if state_1[4] == '0':  # 0 outflow state_1
    #         if state_2[3] != '0':  # no 0 volume gradient state_2
    #             if debug:
    #                 print(f'Invalid state transition (I+(Inflow, Volume), 0 inflow): {state_1} --> {state_2}')
    #             return False

    # # I-(Outflow, Volume)
    # if state_1[4] == '+':  # positive outflow state_1
    #     if state_1[0] == '0':  # 0 inflow state_1
    #         if state_2[3] != '-':  # no negative volume gradient state_2
    #             if debug:
    #                 print(f'Invalid state transition (I-(Outflow, Volume), positive outflow): {state_1} --> {state_2}')
    #             return False
    # elif state_1[4] == 'max':  # max outflow state_1
    #     if state_1[0] == '0':  # 0 inflow state_1
    #         if state_2[3] != '-':  # no negative volume gradient state_2
    #             if debug:
    #                 print(f'Invalid state transition (I-(Outflow, Volume), max outflow, 0 inflow): {state_1} --> {state_2}')
    #             return False
    #     elif state_1[0] == '+':  # positive inflow state_1
    #         if state_2[3] != '-':  # no negative volume gradient state_2
    #             if debug:
    #                 print(f'Invalid state transition (I-(Outflow, Volume), max outflow, positive inflow): {state_1} --> {state_2}')
    #             return False

    # validate that state_1 and state_2 can only be equal if state_1 has a non-zero gradient for an interval magnitude
    if state_1 == state_2:
        if state_1[1] != '0':  # non-zero inflow gradient state_1
            if state_1[0] != '+':  # non-interval inflow state_1
                if debug:
                    print(f'Invalid state transition (non-zero inflow gradient, non-interval inflow): {state_1} --> {state_2}')
                return False
        if state_1[3] != '0':  # non-zero volume gradient state_1
            if state_1[2] != '+':  # non-interval volume state_1
                if debug:
                    print(f'Invalid state transition (non-zero volume gradient, non-interval volume): {state_1} --> {state_2}')
                return False
        elif state_1[5] != '0':  # non-zero outflow gradient state_1
            if state_1[4] != '+':  # non-interval outflow state_1
                if debug:
                    print(f'Invalid state transition (non-zero outflow gradient, non-interval outflow): {state_1} --> {state_2}')
                return False
        else:
            return False

    return True


def get_state_representation(state):
    """
    Get the representation of the state in human-readable form.

    :param state: the state
    :returns: the representation of the state
    """
    return f'Inflow: [{state[0]}, {state[1]}]\nVolume: [{state[2]}, {state[3]}]\nOutflow: [{state[4]}, {state[5]}]'


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
        smoothing='avg_dist', 
        label='Qualitative model')
    
    for state_transition in state_transitions:
        state_1, state_2 = state_transition
        representation_1 = get_state_representation(state_1)
        representation_2 = get_state_representation(state_2)
        graph.add_edge(representation_1, representation_2)

    graph.write('./graph.dot')
    graph.draw('./graph.svg', prog='fdp')
    graph.draw('./graph.png', prog='fdp')