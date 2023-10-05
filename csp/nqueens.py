from __future__ import annotations
from typing import List, Set
from helpers import check_is_value_valid, check_is_value_valid_V2


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
        curr_rules = set()
        while len(self.rules) > 0:
            curr_rule = self.rules.pop(0)
            print(curr_rule.destination.domain, curr_rule.source.domain)
            try:
                if not curr_rule.test_consistency() and len(curr_rule.source.domain) > 0 and len(curr_rule.destination.domain) > 0:
                    self.rules.append(
                        Rule(curr_rule.destination, curr_rule.source))
                    for each_connected in curr_rule.source.connected:
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

    def is_consistent(self: Rule) -> bool:
        if len(self.source.domain) > 1:
            for each_value in self.destination.domain:
                if not check_is_value_valid(self.destination.key, each_value, self.source.key, self.source.domain):
                    self.destination.domain.remove(each_value)
                    return False
            return True

        return True

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

    def get_all_domains(self: StateGraph) -> dict[int, List[int]]:
        old_domains = {}
        for each_variable in self.variables:
            old_domains[each_variable.key] = list(
                x for x in each_variable.domain)
        return old_domains

    def run_algorithm(self: StateGraph) -> None:
        unsatisfied_variables = list(
            self.variables[i] for i in range(self.rows))
        ac3_agenda: Agenda = Agenda()
        bad_choice = -1
        while len(unsatisfied_variables) > 0:
            first_variable = unsatisfied_variables.pop(0)
            choices = list(x for x in first_variable.domain)

            if bad_choice != -1:
                choices = choices[1:] + [choices[0]]
                bad_choice = -1

            optimal_choice = choices.pop(0)

            old_domains = self.get_all_domains()
            first_variable.domain = set([optimal_choice])
            for each_connected in first_variable.connected:
                ac3_agenda.rules.append(Rule(first_variable, each_connected))
                ac3_agenda.rules.append(Rule(each_connected, first_variable))

            is_consistent = ac3_agenda.check_arc_consistency()
            if not is_consistent or not all((len(x.domain) > 0 for x in self.variables)):
                bad_choice = optimal_choice
                for each_key in old_domains.items():
                    self.variables[each_key[0] -
                                   1].domain = set(each_key[1])
                unsatisfied_variables.insert(0, first_variable)
        for each_var in self.variables:
            print(each_var.domain)


if __name__ == '__main__':
    board = StateGraph(6, 6)
    board.run_algorithm()
