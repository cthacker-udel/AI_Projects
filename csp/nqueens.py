from __future__ import annotations
from typing import Dict, List

class BoardCoordinate:
    def __init__(self: BoardCoordinate, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.occupied: bool = False
    
    def occupy(self: BoardCoordinate) -> None:
        self.occupied = not self.occupied

class BoardDomain:
    def __init__(self: BoardDomain, row: int, cols: int) -> None:
        self.domain_key = row
        self.domain: Dict[int, BoardCoordinate] = {}
        for each_col in range(1, cols + 1):
            self.domain[each_col] = BoardCoordinate(row, each_col)
        

class Board:
    def __init__(self: Board, m: int = 5, n: int = 5) -> None:
        self.rows = m
        self.columns = n
        self.domains: List[BoardDomain] = []
        for each_row in range(1, self.rows + 1):
            self.domains.append(BoardDomain(each_row, self.columns))
        

    def find_domain(self: Board, row: int) -> BoardDomain:
        for each_domain in self.domains:
            if each_domain.domain_key == row:
                return each_domain
        raise Exception("Cannot find domain")
    

    def place_queen(self: Board, queen_x: int, queen_y: int) -> None:
        found_domain = self.find_domain(queen_x)
        if queen_y in found_domain.domain and not found_domain.domain[queen_y].occupied:
            # can place there
            found_domain.domain[queen_y].occupy()


    def update_diagonals(self: Board, queen_x: int, queen_y: int, down: bool = False, right: bool = False) -> None:
        col = queen_y - (-1 if right else 1)
        for i in range(queen_x - (-1 if down else 1), self.rows if down else 0):
            found_domain = self.find_domain(i)
            if found_domain.domain[col].occupied:
                return False

            if (col == self.columns and right) or (col == 0 and not right):
                return True
            
            found_domain.domain[col].occupy()
        return True
    
    def update_horizontal(self: Board, queen_x: int) -> None:
        found_domain = self.find_domain(queen_x)
        for each_x in found_domain.domain:
            if each_x != queen_x:
                found_domain.domain[each_x].occupy()
    
    def update_vertical(self: Board, queen_y: int) -> None:
        for i in range(0, self.rows):
            found_domain = self.find_domain(i)
            if found_domain.domain[queen_y].occupied:
                return False
            
            found_domain.domain[queen_y].occupy()
        return True
            


if __name__ == '__main__':
    board = Board()