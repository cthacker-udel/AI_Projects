from __future__ import annotations
from typing import List, Set


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


class BoardVariable:
    def __init__(self: BoardVariable, row: int, cols: int) -> None:
        self.key = row
        self.cols = cols
        self.domain: Set[int] = set(x for x in range(1, cols + 1))
        self.connected: List[BoardVariable] = []

    def clone(self: BoardVariable) -> BoardVariable:
        cloned = BoardVariable(self.key, self.cols)
        cloned.domain = set(x for x in self.domain)
        cloned.connected = list(x.clone() for x in self.connected)

        return cloned


class Agenda:
    def __init__(self: Agenda):
        self.rules: List[Rule] = []

    def check_arc_consistency(self: Agenda) -> bool:
        while len(self.rules) > 0:
            curr_rule = self.rules.pop(0)
            try:
                if not curr_rule.is_consistent():
                    self.rules.append(
                        Rule(curr_rule.destination, curr_rule.source))
            except ValueError as err:
                print(err)
                return False
        return True


class Rule:
    def __init__(self: Rule, _from: BoardVariable, _to: BoardVariable):
        self.source: BoardVariable = _from
        self.destination: BoardVariable = _to

    def is_consistent(self: Rule) -> bool:
        if len(self.source.domain) > 1:
            return True

        diag_right = self.destination.key + list(self.source.domain)[0] - 1
        diag_left = list(self.source.domain)[0] - (self.destination.key - 1)
        col = list(self.source.domain)[0]

        tmp_domain = set(x for x in self.destination.domain)
        diff = set([diag_right, diag_left, col])

        if len(tmp_domain.difference(diff)) == 0:
            raise ValueError("Domain will be empty")

        is_consistent_b = True

        if diag_right in self.destination.domain:
            self.destination.domain.remove(diag_right)
            is_consistent_b = False
        if diag_left in self.destination.domain:
            self.destination.domain.remove(diag_left)
            is_consistent_b = False
        if col in self.destination.domain:
            self.destination.domain.remove(col)
            is_consistent_b = False
        return is_consistent_b

    def __str__(self: Rule) -> str:
        return f'{generate_id_from_key(self.source.key)} --> {generate_id_from_key(self.destination.key)}'


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

    def potential_impact(self: StateGraph, row: int, col: int) -> int:
        cols = list(x for x in range(1, col)) + \
            list(x for x in range(col + 1, self.columns + 1))
        diag_left = list(x for x in range(col + 1, self.columns + 1))
        diag_right = list(x for x in range(0, col))

        # potential # of domain values that will be removed
        return len(cols) + len(diag_left) + len(diag_right)

    def run_algorithm(self: StateGraph) -> None:
        unsatisfied_variables = list(
            self.variables[i] for i in range(self.rows))
        ac3_agenda: Agenda = Agenda()
        while len(unsatisfied_variables) > 0:
            first_variable = unsatisfied_variables.pop(0)
            choices = sorted(list(x for x in first_variable.domain),
                             key=lambda x: self.potential_impact(first_variable.key, x))
            optimal_choice = choices.pop(0)
            first_variable.domain = set([optimal_choice])
            for each_connected in first_variable.connected:
                ac3_agenda.rules.append(Rule(first_variable, each_connected))
            is_consistent = ac3_agenda.check_arc_consistency()
            if not is_consistent:
                first_variable.domain = set(choices) - first_variable.domain


if __name__ == '__main__':
    board = StateGraph()
    board.run_algorithm()
