from __future__ import annotations
from typing import List, Optional
from enum import Enum
from random import randint
from graph import GraphNode, GraphNodeType


def generate_checkers_board(rows: int, cols: int) -> List[List[BoardPiece]]:
    board: List[List[BoardPiece]] = []
    for i in range(1, rows + 1):
        board_row: List[BoardPiece] = []
        for j in range(1, cols + 1):
            board_row.append(BoardPiece(i, j))
        board.append(board_row[:])
        board_row = []
    return board


class CheckersPlayer(Enum):
    BOTTOM = 0,
    TOP = 1


class CheckersPiece:
    def __init__(self: CheckersPiece, owner: CheckersPlayer, x: int, y: int, rows: int = 0, cols: int = 0):
        self.owner: CheckersPlayer = owner
        self.x = x
        self.y = y
        self.is_king = False
        self.value = 0
        self.rows = rows
        self.cols = cols

    def compute_heuristic_value(self: CheckersPiece) -> None:
        # Material count
        self.value += 2 if self.is_king else 1

        # King's position
        opponents_kings_row_start = 0 if self.owner == CheckersPlayer.TOP else 5
        opponents_kings_row_end = 2 if self.owner == CheckersPlayer.TOP else self.rows - 1
        # Is in opponents territory
        if self.is_king and self.y <= opponents_kings_row_end and self.y >= opponents_kings_row_start:
            # Configure for any row size
            col_bound_left = 0
            col_bound_right = self.cols - 1
            center_opponent_x = (opponents_kings_row_end +
                                 opponents_kings_row_start) // 2
            center_opponent_y = (col_bound_left + col_bound_right) // 2
            # add - 10 to make sure the distance is +10 when it is right on the center
            self.value += abs(abs(self.x - center_opponent_x) +
                              abs(self.y - center_opponent_y) - 10)

        # Control of the center
        center_board_row = self.rows // 2
        center_board_col = self.cols // 2
        distance_center = abs(self.y - center_board_col) + \
            abs(self.x - center_board_row)
        self.value += distance_center

        # King's Row
        if not self.is_king and not (self.y <= opponents_kings_row_end and self.y >= opponents_kings_row_start):
            # compute distance to kings row
            dist_to_kings_row = abs(self.y - opponents_kings_row_start)
            self.value += dist_to_kings_row

        # Piece Advancement
        if self.y <= (opponents_kings_row_start + 1):
            self.value += abs(self.y - (opponents_kings_row_end + 1))

        # Mobility (used in the board instance)
        # Threat Assessment (used in board instance)
        # Safety (used in board instance)
        # Forced Jumps (used in board instance)
        # Board control (used in board instance)

    def clone(self: CheckersPiece) -> CheckersPiece:
        cloned = CheckersPiece(self.owner, self.x, self.y)
        return cloned


class BoardPiece:
    def __init__(self: BoardPiece, x: int, y: int) -> None:
        self.piece: Optional[CheckersPiece] = None
        self.x = x
        self.y = y

    def place_piece(self: BoardPiece, checkers_piece: CheckersPiece) -> None:
        self.piece = checkers_piece

    def clone(self: BoardPiece) -> BoardPiece:
        cloned = BoardPiece(self.x, self.y)
        cloned.piece = self.piece.clone() if self.piece else None
        return cloned


class CheckersState:
    def __init__(self: CheckersState, rows: int, cols: int, curr_turn: Optional[CheckersPlayer] = None, curr_board: Optional[List[BoardPiece]] = None) -> None:
        self.turn: CheckersPlayer = [CheckersPlayer.BOTTOM, CheckersPlayer.TOP][randint(
            0, 1)] if not curr_turn else curr_turn
        self.board: List[List[BoardPiece]] = [[x.clone() for x in self.board[y]] for y in range(rows)] if curr_board else generate_checkers_board(
            rows, cols)
        self.rows = rows
        self.cols = cols


def init_board(state: CheckersState) -> CheckersState:
    both_side_size = state.rows - 2
    odds = True
    players = [CheckersPlayer.BOTTOM, CheckersPlayer.TOP]
    player = 0

    for i in range(0, both_side_size):
        for j in range(0 if odds else 1, state.cols, 2):
            state.board[i][j].place_piece(CheckersPiece(
                players[player], j, i, state.rows, state.cols))
        odds = not odds

    player += 1
    for i in range(0, both_side_size):
        for j in range(0 if odds else 1, state.cols, 2):
            state.board[-1 * (i + 1)
                        ][j].place_piece(CheckersPiece(players[player], j, i, state.rows, state.cols))
        odds = not odds

    return state


class CheckersGraphNode(GraphNode):
    def __init__(self: CheckersGraphNode) -> None:
        super().__init__()
        self.state: Optional[CheckersState] = None

    def set_state(self: CheckersGraphNode, state: CheckersState) -> None:
        self.state = state

    def is_goal_state(self: CheckersGraphNode) -> bool:
        if self.state is None:
            return False

        board_pieces = self.state.board
        player_count = {}
        for each_board_row in board_pieces:
            for each_tile in each_board_row:
                if each_tile.piece != None:
                    if each_tile.piece.owner in player_count:
                        player_count[each_tile.piece.owner] += 1
                    else:
                        player_count[each_tile.piece.owner] = 1
        # only 1 player left on board
        return len(player_count.keys()) == 1

    def run_algorithm(self: CheckersGraphNode) -> None:

        if self.state is None:
            return None

        turn = self.state.turn
        move_queue = [self.state]
        while len(move_queue) > 0:
            # DFS
            curr_move = move_queue.pop()


if __name__ == '__main__':
    g: CheckersGraphNode = CheckersGraphNode().set_spec(
        GraphNodeType.MAX)  # type: ignore
    g.state = CheckersState(8, 8)
