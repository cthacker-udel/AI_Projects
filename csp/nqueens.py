from __future__ import annotations
from typing import List, Set, Optional
from helpers import check_is_value_valid_V2


def filter_out_connected(key: int, node: BoardVariable) -> List[BoardVariable]:
    filtered_connections: List[BoardVariable] = [node]
    for each_node in node.connected:
        if each_node.key == key:
            continue
        filtered_connections.append(each_node)
    return filtered_connections


def generate_id_from_key(key: int) -> str:
    """
        # Excel formula https://stackoverflow.com/a/182924
    """
    column_name = ''
    while key > 0:
        mod = (key - 1) % 36
        column_name = chr(ord('A') + mod) + column_name
        key = (key - mod) // 26
    return column_name

# BEGIN ARC CONSISTENCY


class Agenda:
    def __init__(self: Agenda):
        self.rules: List[Rule] = []

    def check_arc_consistency(self: Agenda) -> bool:
        curr_rules = set()
        while len(self.rules) > 0:
            curr_rule = self.rules.pop(0)
            try:
                if not curr_rule.test_consistency() and len(curr_rule.source.domain) > 0 and len(curr_rule.destination.domain) > 0:
                    self.rules.append(
                        Rule(curr_rule.destination, curr_rule.source))
                    for each_connected in filter_out_connected(curr_rule.source.key, curr_rule.destination):
                        potential_rule = Rule(curr_rule.source, each_connected)
                        if each_connected.key != curr_rule.destination.key and str(potential_rule) not in curr_rules:
                            self.rules.append(
                                potential_rule)
                            curr_rules.add(str(potential_rule))
                elif str(curr_rule) in curr_rules:
                    curr_rules.remove(str(curr_rule))

            except ValueError as err:
                print(err)
                return False
        return True


class Rule:
    def __init__(self: Rule, _from: BoardVariable, _to: BoardVariable):
        self.source: BoardVariable = _from
        self.destination: BoardVariable = _to

    def test_consistency(self: Rule) -> bool:
        if len(self.destination.domain) > 0:
            tmp_domain = set(self.source.domain)
            for each_value in self.source.domain:
                is_valid_value = True
                for each_potential_valid_assignment in self.destination.domain:
                    if check_is_value_valid_V2(self.source.key, each_value, self.destination.key, each_potential_valid_assignment):
                        is_valid_value = True
                        break
                    else:
                        is_valid_value = False
                if not is_valid_value:
                    tmp_domain.remove(each_value)

            if tmp_domain != self.source.domain:
                self.source.domain = tmp_domain
                return False

            return True
        return False

    def __str__(self: Rule) -> str:
        return f'{generate_id_from_key(self.source.key)} --> {generate_id_from_key(self.destination.key)}'

# END ARC CONSISTENCY


class BoardVariable:
    def __init__(self: BoardVariable, row: int, cols: int, domain: Optional[Set[int]] = None, connected: Optional[List[BoardVariable]] = None) -> None:
        self.key = row
        self.cols = cols
        self.domain: Set[int] = set(x for x in range(
            1, cols + 1)) if not domain else set(domain)
        self.connected: List[BoardVariable] = [
        ] if not connected else connected

    def clone(self: BoardVariable, connected_exclusion_id: Optional[int] = None) -> BoardVariable:
        cloned = BoardVariable(self.key, self.cols)
        cloned.domain = set(x for x in self.domain)
        connected_map: dict[int, set[int]] = {}
        cloned.connected = []
        for each_variable in self.connected:
            if connected_exclusion_id is not None and connected_exclusion_id == each_variable.key:
                connected_map[self.key] = set(self.domain)
                continue
            connected_map[each_variable.key] = set(each_variable.domain)

        for [each_connected_key, each_connected_domain] in connected_map.items():
            cloned.connected.append(BoardVariable(
                each_connected_key, self.cols, each_connected_domain))

        return cloned

    def __str__(self: BoardVariable) -> str:
        return f'|{self.key}|-->{"".join(list(str(x) for x in self.domain))}'


class StateNode:
    def __init__(self: StateNode, variable: BoardVariable, variable_count: int) -> None:
        # TODO: Represent choices of queens as nodes in the state, so the first layer is 1,1 | 1,2 | 1,3 | 1,4 | 1,5, then from those roots, branch down
        self.parent: Optional[StateNode] = None
        self.x_move = variable.key
        self.explored = False
        self.variable = variable.clone()
        self.variable.connected = [BoardVariable(
            x.key, x.cols, set(x.domain)) for x in self.variable.connected]
        self.y_move = -1
        self.variable_count = variable_count

    def move(self: StateNode, y_move: int) -> StateNode:
        self.y_move = y_move
        self.variable.domain = set([y_move])
        return StateNode(self.variable.clone(), self.variable_count)

    def find_next_move(self: StateNode) -> BoardVariable:
        for each_variable_id in range(self.variable.key + 1, self.variable_count + 1):
            for each_variable in self.variable.connected:
                if each_variable.key == each_variable_id:
                    # found variable
                    each_variable.connected = self.variable.clone(
                        each_variable.key).connected
                    return each_variable

        # fallback case
        return self.variable

    def __str__(self: StateNode) -> str:
        total_str = ''
        for each_variable_id in range(1, self.variable_count + 1):
            for each_variable in [self.variable] + self.variable.connected:
                if each_variable.key == each_variable_id:
                    total_str += str(each_variable)
        return total_str


class StateGraph:
    def __init__(self: StateGraph, m: int = 5, n: int = 5) -> None:
        self.rows = m
        self.columns = n
        self.moves: List[List[int]]
        self.variables: List[BoardVariable] = []
        for each_row in range(1, self.rows + 1):
            self.variables.append(BoardVariable(each_row, self.columns))
        for ind, each_variable in enumerate(self.variables):
            each_variable.connected = self.variables[:ind] + \
                self.variables[ind + 1:]

    def is_goal(self: StateGraph, node: StateNode) -> bool:
        total_variables = [node.variable] + node.variable.connected
        return len(list(filter(lambda x: len(x.domain) == 1, total_variables))) == len(total_variables)

    def print_moves(self: StateGraph, node: StateNode) -> None:
        total_variables = [node.variable] + node.variable.connected

        domain_mapping: dict[int, set[int]] = {}

        for i in range(1, self.rows + 1):
            for each_node in total_variables:
                if each_node.key == i:
                    domain_mapping[i] = each_node.domain

        print_str = ''
        for i in range(1, self.rows + 1):
            print_str += f'{generate_id_from_key(i)} = {domain_mapping[i]}\n'
        print(print_str)

    def run_algorithm(self: StateGraph) -> None:
        # stack, LIFO
        move_stack: List[StateNode] = []
        explored_states: set[str] = set()

        for each_root_domain_value in self.variables[0].domain:
            move_stack.append(
                StateNode(self.variables[0], self.rows).move(each_root_domain_value))

        while len(move_stack) > 0:
            current_move = move_stack.pop()

            if not current_move.explored and str(current_move) not in explored_states:
                current_move.explored = True
                explored_states.add(str(current_move))
                ac3_agenda = Agenda()
                for each_connected in current_move.variable.connected:
                    # because it adds a rule with each_connected's .connected field having 0 values
                    ac3_agenda.rules.append(
                        Rule(current_move.variable, each_connected))
                    ac3_agenda.rules.append(
                        Rule(each_connected, current_move.variable))
                is_consistent = ac3_agenda.check_arc_consistency()
                if is_consistent:
                    next_move = StateNode(
                        current_move.find_next_move(), self.rows)
                    next_move.parent = current_move

                    for each_value in next_move.variable.domain:
                        new_move = next_move.move(each_value)
                        move_stack.append(new_move)
                if self.is_goal(current_move) and is_consistent:
                    self.print_moves(current_move)
                    break
        print('exited')


if __name__ == '__main__':
    board = StateGraph(30, 30)
    board.run_algorithm()
