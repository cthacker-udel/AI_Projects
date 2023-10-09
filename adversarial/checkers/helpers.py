def generate_diag(row: int, col: int, down: bool = False, left: bool = False) -> Tuple[int, int]:
    return (row - (-1 if down else 1), col - (1 if left else -1))