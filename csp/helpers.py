from typing import Set, Tuple

# NQUEENS


def generate_diag(row: int, col: int, down: bool = False, left: bool = False) -> Tuple[int, int]:
    return (row - (-1 if down else 1), col - (1 if left else -1))


def generate_col(row: int, col: int, down: bool = False) -> Tuple[int, int]:
    return (row - (-1 if down else 1), col)


def does_diagonal_hit(row: int, col: int, source_row: int, source_col: int, down: bool = False, left: bool = False) -> bool:
    tmp_row = row
    tmp_col = col
    while row != source_row and row > 0:
        if row < source_row:
            row += 1
        else:
            row -= 1
        tmp_row += (1 if down else -1)
        tmp_col += (-1 if left else 1)
    return tmp_row == row and tmp_col == source_col


def does_col_hit(col: int, source_col: int) -> bool:
    return source_col == col


def check_diagonal(row: int, col: int, source_row: int, source_col: int) -> bool:
    return does_diagonal_hit(row, col, source_row, source_col, True) or does_diagonal_hit(row, col, source_row, source_col, True, True) or does_diagonal_hit(row, col, source_row, source_col, False, True) or does_diagonal_hit(row, col, source_row, source_col)


def check_is_value_valid(value_row: int, value_col: int, source_row: int, source_domain: Set[int]) -> bool:
    for source_col in source_domain:
        if not (check_diagonal(value_row, value_col, source_row, source_col) or does_col_hit(value_col, source_col)):
            return True
    return False


def check_is_value_valid_V2(value_row: int, value_col: int, source_row: int, source_value: int) -> bool:
    if not (check_diagonal(value_row, value_col, source_row, source_value) or does_col_hit(value_col, source_value)):
        return True
    return False
