from __future__ import annotations
from typing import Optional
from enum import Enum
from random import randint
from graph import GraphNode, GraphNodeType

# HELPERS


def generate_checkers_board(rows: int, cols: int) -> list[list[BoardPiece]]:
    board: list[list[BoardPiece]] = []
    for i in range(1, rows + 1):
        board_row: list[BoardPiece] = []
        for j in range(1, cols + 1):
            board_row.append(BoardPiece(i, j))
        board.append(board_row[:])
        board_row = []
    return board


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


def calculate_vulnerable_points(piece: CheckersPiece, board: CheckersState) -> int:
    coord_x = piece.x
    coord_y = piece.y

    coord_x_lower_left, coord_y_lower_left, coord_y_upper_left, coord_x_upper_left, coord_x_upper_right, coord_y_upper_right, coord_y_lower_right, coord_x_lower_right = 0, 0, 0, 0, 0, 0, 0, 0

    threats = 0

    # upper left --> lower right
    try:
        coord_x_upper_left = coord_x - 1
        coord_y_upper_left = coord_y + 1
        coord_x_lower_right = coord_x + 1
        coord_y_lower_right = coord_y - 1
        is_threat = board.board[coord_y_upper_left][coord_x_upper_left].piece.owner != piece.owner and board.board[coord_y_lower_right][coord_x_lower_right].piece is None
        threats += 1 if is_threat else 0
    except:
        pass

    # upper right --> lower left
    try:
        coord_x_upper_right = coord_x + 1
        coord_y_upper_right = coord_y + 1
        coord_x_lower_left = coord_x - 1
        coord_y_lower_left = coord_y - 1
        is_threat = board.board[coord_y_upper_right][coord_x_upper_right].piece.owner != piece.owner and board.board[coord_y_lower_left][coord_x_lower_left] is None
        threats += 1 if is_threat else 0
    except:
        pass

    # IF KING lower left --> upper right
    try:
        is_threat = board.board[coord_y_lower_left][coord_x_lower_left].piece.owner != piece.owner and board.board[
            coord_y_lower_left][coord_x_lower_left].piece.is_king and board.board[coord_y_upper_right][coord_x_upper_right] is None
        threats += 1 if is_threat else 0
    except:
        pass

    # IF KING lower right --> upper left
    try:
        is_threat = board.board[coord_y_lower_right][coord_x_lower_right].piece.owner != piece.owner and board.board[
            coord_y_lower_right][coord_x_lower_right].piece.is_king and board.board[coord_y_upper_left][coord_x_upper_left] is None
        threats += 1 if is_threat else 0
    except:
        pass

    return threats


def calculate_safe_positions(piece: CheckersPiece, board: CheckersState) -> int:
    # safe being not in the diagonal path, or having a piece in the diagonal where it would land if it jumps

    safe_points = 0
    coord_x = piece.x
    coord_y = piece.y

    coord_x_upper_left = coord_x - 1
    coord_y_upper_left = coord_y + 1
    coord_x_lower_right = coord_x + 1
    coord_y_lower_right = coord_y - 1
    coord_x_upper_right = coord_x + 1
    coord_y_upper_right = coord_y + 1
    coord_x_lower_left = coord_x - 1
    coord_y_lower_left = coord_y - 1
    coord_x_left = coord_x - 1
    coord_x_right = coord_x + 1
    coord_y_above = coord_y - 1
    coord_y_below = coord_y + 1

    # upper left --> lower right
    try:
        is_safe = board.board[coord_y_upper_left][coord_x_upper_left].piece.owner != piece.owner and board.board[
            coord_y_lower_right][coord_x_lower_right].piece is not None
        safe_points += 1 if is_safe else 0
    except:
        pass

    # upper right --> lower left
    try:
        is_safe = board.board[coord_y_upper_right][coord_x_upper_right].piece.owner != piece.owner and board.board[coord_y_lower_left][coord_x_lower_left] is not None
        safe_points += 1 if is_safe else 0
    except:
        pass

    # IF KING lower left --> upper right
    try:
        is_safe = board.board[coord_y_lower_left][coord_x_lower_left].piece.owner != piece.owner and board.board[
            coord_y_lower_left][coord_x_lower_left].piece.is_king and board.board[coord_y_upper_right][coord_x_upper_right] is not None
        safe_points += 1 if is_safe else 0
    except:
        pass

    # IF KING lower right --> upper left
    try:
        is_safe = board.board[coord_y_lower_right][coord_x_lower_right].piece.owner != piece.owner and board.board[
            coord_y_lower_right][coord_x_lower_right].piece.is_king and board.board[coord_y_upper_left][coord_x_upper_left] is not None
        safe_points += 1 if is_safe else 0
    except:
        pass

    # above
    try:
        is_safe = board.board[coord_y_above][coord_x].piece.owner != piece.owner
        safe_points += 1 if is_safe else 0
    except:
        pass

    # below
    try:
        is_safe = board.board[coord_y_below][coord_x].piece.owner != piece.owner
        safe_points += 1 if is_safe else 0
    except:
        pass

    # right
    try:
        is_safe = board.board[coord_y][coord_x_right].piece.owner != piece.owner
        safe_points += 1 if is_safe else 0
    except:
        pass

    # left
    try:
        is_safe = board.board[coord_y][coord_x_left].piece.owner != piece.owner
        safe_points += 1 if is_safe else 0
    except:
        pass

    return safe_points


def is_forced_jump(piece: CheckersPiece, board: CheckersState) -> bool:
    return calculate_vulnerable_points(piece, board) > 0


def sort_states_by_heuristic(states: list[CheckersState]) -> list[CheckersState]:
    return sorted(states, key=lambda x: x.generate_heuristic())

# END HELPERS


class CheckersPlayer(Enum):
    """
    Represents a checkers player instance

    Args:
        Enum (_type_): Used for constructing a enum in python, have to create a custom class inheriting from the enum class
    """
    BOTTOM = 0,
    TOP = 1


class CheckersPiece:
    """
    Represents a checkers piece, aka an actual piece the user can play with

    Arguments:
        self (CheckersPiece): The internal state
        owner (CheckersPlayer): The owner of the checkers piece
        x (int): The x coordinate of the checkers piece
        y (int): The y coordinate of the checkers piece
        rows (int): The total amount of rows in the board
        cols (int): The total amount of columns in the board

    Returns:
        Created instance
    """

    def __init__(self: CheckersPiece, owner: CheckersPlayer, x: int, y: int, rows: int = 0, cols: int = 0):
        self.owner: CheckersPlayer = owner
        self.x = x
        self.y = y
        self.is_king = False
        self.value = 0
        self.rows = rows
        self.cols = cols

    def compute_heuristic_value(self: CheckersPiece) -> int:
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

        return self.value

    def clone(self: CheckersPiece) -> CheckersPiece:
        cloned = CheckersPiece(self.owner, self.x, self.y)
        return cloned


class BoardPiece:
    """
    Represents a cell (square) on the board, can be injected with a CheckersPiece instance

    Arguments:
        self (BoardPiece): The internal state
        x (int): The x coordinate
        y (int): The y coordinate

    Returns:
        The board square
    """

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


class CheckersMove:
    """
    Represents the outline of a move in checkers

    Arguments:
        self (CheckersMove): The internal state
        board (list[list[BoardPiece]]): Represents a 2D array of board pieces
        from_x (int): The x coordinate where the piece is originating from
        from_y (int): The y coordinate where the piece is originating from
        to_x (int): The x coordinate where the piece is traveling to
        to_y (int): The y coordinate where the piece is traveling to
        capture (bool): Whether the piece is captured (field will be removed in future versions)
    """

    def __init__(self: CheckersMove, board: list[list[BoardPiece]], from_x: int, from_y: int, to_x: int, to_y: int, capture: bool = False):
        self.board = board
        self.from_x = from_x
        self.from_y = from_y
        self.to_x = to_x
        self.to_y = to_y
        self.capture = capture


class CheckersState:
    """
    Represents a node in the state tree, a snapshot of the state of the game

    Arguments:
        self (CheckersState): The internal state
        rows (int): The # of rows in the board
        cols (int): The # of columns in the board
        curr_turn (Optional[CheckersPlayer]): The player who controls the current turn in the game
        curr_board (Optional[list[BoardPiece]]): The current board in play

    Returns:
        The checkers state instance
    """

    def __init__(self: CheckersState, rows: int, cols: int, curr_turn: Optional[CheckersPlayer] = None, curr_board: Optional[list[list[BoardPiece]]] = None) -> None:
        self.turn: CheckersPlayer = [CheckersPlayer.BOTTOM, CheckersPlayer.TOP][randint(
            0, 1)] if not curr_turn else curr_turn
        self.board: list[list[BoardPiece]] = [[x.clone() for x in self.board[y]] for y in range(rows)] if curr_board else generate_checkers_board(
            rows, cols)
        self.rows = rows
        self.cols = cols
        self.value = 0
        self.moves: list[CheckersMove] = []
        self.explored: bool = False
        self.parent: Optional[CheckersState] = None
        self.depth = 1

    def next_turn(self: CheckersState) -> None:
        self.turn = CheckersPlayer.BOTTOM if self.turn == CheckersPlayer.TOP else CheckersPlayer.TOP

    def clone(self: CheckersState) -> CheckersState:
        cloned_state = CheckersState(
            self.rows, self.cols, self.turn, self.board)
        cloned_state.value = self.value
        cloned_state.explored = self.explored

        return cloned_state

    def clone_board(self: CheckersState) -> list[list[BoardPiece]]:
        cloned_board: list[list[BoardPiece]] = []
        for each_row in self.board:
            sub_row = []
            for each_board_tile in each_row:
                sub_row.append(each_board_tile.clone())
            cloned_board.append(sub_row)
            sub_row = []
        return cloned_board

    def process_move(self: CheckersState, move: CheckersMove) -> CheckersState:
        cloned_state = self.clone()
        cloned_state.explored = False

        moving_piece = cloned_state.board[move.from_y][move.from_x]
        del cloned_state.board[move.from_y][move.from_x]

        cloned_state.board[move.to_y][move.to_x] = moving_piece
        cloned_state.next_turn()
        cloned_state.depth += 1
        return cloned_state

    def process_moves(self: CheckersState) -> list[CheckersState]:
        processed_moves: list[CheckersState] = []
        for each_move in self.moves:
            processed_moves.append(self.process_move(each_move))
        return processed_moves

    def generate_potential_moves(self: CheckersState) -> list[CheckersMove]:
        curr_turn_pieces: list[CheckersPiece] = []
        cloned_board = self.clone_board()
        for each_board_row in cloned_board:
            for each_board_tile in each_board_row:
                # current piece owner is the current turn's player
                if each_board_tile.piece is not None and each_board_tile.piece.owner == self.turn:
                    curr_turn_pieces.append(each_board_tile.piece)

        potential_moves: list[CheckersMove] = []
        for each_owner_piece in curr_turn_pieces:
            piece_x = each_owner_piece.x
            piece_y = each_owner_piece.y
            if each_owner_piece.is_king:
                try:
                    # DIAG DOWN LEFT
                    diag_down_left_x = piece_x - 1
                    diag_down_left_y = piece_y - 1
                    if cloned_board[diag_down_left_x][diag_down_left_y].piece is not None and cloned_board[diag_down_left_x][diag_down_left_y].piece.owner != self.turn:  # type: ignore
                        # check if is opponents, then check for jump
                        if cloned_board[diag_down_left_x - 1][diag_down_left_y - 1] is None:
                            # can make jump
                            potential_moves.append(CheckersMove(self.clone_board(
                            ), piece_x, piece_y, diag_down_left_x - 1, diag_down_left_y - 1, True))
                except:
                    pass

                try:
                    # DIAG DOWN RIGHT
                    diag_down_right_x = piece_x + 1
                    diag_down_right_y = piece_y - 1
                    if cloned_board[diag_down_right_x][diag_down_right_y].piece is not None and cloned_board[diag_down_right_x][diag_down_right_y].piece.owner != self.turn:  # type: ignore
                        # check if is opponents, then check for jump
                        if cloned_board[diag_down_right_x + 1][diag_down_right_y - 1] is None:
                            potential_moves.append(CheckersMove(self.clone_board(
                            ), piece_x, piece_y, diag_down_right_x + 1, diag_down_right_y - 1, True))
                except:
                    pass

            else:
                try:
                    # DIAG UP LEFTS
                    diag_up_left_x = piece_x - 1
                    diag_up_left_y = piece_y + 1
                    if cloned_board[diag_up_left_x][diag_up_left_y].piece is not None and cloned_board[diag_up_left_x][diag_up_left_y].piece.owner != self.turn:  # type: ignore
                        # check if is opponents, then check for jump
                        if cloned_board[diag_up_left_x - 1][diag_up_left_y + 1].piece is None:
                            # can make jump
                            potential_moves.append(CheckersMove(self.clone_board(
                            ), piece_x, piece_y, diag_up_left_x - 1, diag_up_left_y + 1, True))
                except:
                    pass

                try:
                    # DIAG UP RIGHT
                    diag_up_right_x = piece_x + 1
                    diag_up_right_y = piece_y + 1
                    if cloned_board[diag_up_right_x][diag_up_right_y].piece is not None and cloned_board[diag_up_right_x][diag_up_right_y].piece.owner != self.turn:  # type: ignore
                        # check if is opponents, then check for jump
                        if cloned_board[diag_up_right_x + 1][diag_up_right_y + 1] is None:
                            # can make jump
                            potential_moves.append(CheckersMove(self.clone_board(
                            ), piece_x, piece_y, diag_up_right_x + 1, diag_up_right_y + 1, True))
                except:
                    pass
        self.moves = potential_moves
        return potential_moves

    def total_vulnerable_positions(self: CheckersState) -> int:
        your_pieces = []
        for each_board_row in self.board:
            for each_cell in each_board_row:
                if each_cell.piece is not None and each_cell.piece.owner == self.turn:
                    # found your piece
                    your_pieces.append(each_cell.piece)

        # compiled a list of your pieces, now check the diagonals
        total_vulnerable_positions = 0

        for each_piece in your_pieces:
            total_vulnerable_positions += calculate_vulnerable_points(
                each_piece, self)
        return total_vulnerable_positions

    def total_safe_positions(self: CheckersState) -> int:
        your_pieces = []
        for each_board_row in self.board:
            for each_cell in each_board_row:
                if each_cell.piece is not None and each_cell.piece.owner == self.turn:
                    # found your piece
                    your_pieces.append(each_cell.piece)

        total_safe_positions = 0

        for each_piece in your_pieces:
            total_safe_positions += calculate_safe_positions(each_piece, self)

        return total_safe_positions

    def total_forced_jumps(self: CheckersState) -> int:
        your_pieces = []
        for each_board_row in self.board:
            for each_cell in each_board_row:
                if each_cell.piece is not None and each_cell.piece.owner == self.turn:
                    # found your piece
                    your_pieces.append(each_cell.piece)

        total_jumps = 0

        for each_piece in your_pieces:
            total_jumps += is_forced_jump(each_piece, self)

        return total_jumps

    def calculate_board_control(self: CheckersState) -> int:
        your_pieces = []
        enemy_pieces = []
        for each_board_row in self.board:
            for each_cell in each_board_row:
                if each_cell.piece is not None and each_cell.piece.owner == self.turn:
                    # found your piece
                    your_pieces.append(each_cell.piece)
                elif each_cell.piece is not None:
                    enemy_pieces.append(each_cell.piece)
        return len(your_pieces) - len(enemy_pieces)

    def calculate_total_pieces_heuristic(self: CheckersState) -> int:
        your_pieces: list[CheckersPiece] = []
        for each_board_row in self.board:
            for each_cell in each_board_row:
                if each_cell.piece is not None and each_cell.piece.owner == self.turn:
                    # found your piece
                    your_pieces.append(each_cell.piece)

        total_heuristic = 0

        for each_piece in your_pieces:
            total_heuristic += each_piece.compute_heuristic_value()

        return total_heuristic

    def generate_heuristic(self: CheckersState) -> int:
        # Mobility (used in the board instance) DONE
        # Threat Assessment (used in board instance)
        # Safety (used in board instance)
        # Forced Jumps (used in board instance)
        # Board control (used in board instance)

        # Mobility
        self.value += len(self.moves)

        # Threat Assessment
        self.value -= self.total_vulnerable_positions()

        # Safety
        self.value += self.total_safe_positions()

        # Forced jumps
        self.value += self.total_forced_jumps()

        # Board Control
        self.value += self.calculate_board_control()

        # Material Count
        # King's Position
        # Control of the Center
        self.value += self.calculate_total_pieces_heuristic()

        return self.value


class CheckersGraphNode(GraphNode):
    """
    Represents the base graph node class that constructs the checkers graph node, takes in an internal state, allows for customization of which kind of node it is (MIN, MAX, ESTIMAX)

    Args:
        GraphNode (_type_): The internal state, used for the super constructor

    Returns:
        The instantiated state
    """

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

    def run_iterative_deepening_dfs(self: CheckersGraphNode, depth: int) -> None:

        if self.state is None:
            return None

        move_queue = [self.state]
        while len(move_queue) > 0:
            # DFS
            curr_move = move_queue.pop()
            if not curr_move.explored and curr_move.depth < depth:
                curr_move.generate_potential_moves()
                applied_moves = sort_states_by_heuristic(
                    curr_move.process_moves())
                print('applied moves = ', applied_moves)
                for each_move in applied_moves:
                    move_queue.append(each_move)
                    each_move.parent = curr_move
                    # pause when moves are ~x depth down, then structure minimax tree for selection of moves to execute
        print('done')


if __name__ == '__main__':
    # Adversarial network, calculates a strategy (policy) which recommends a move for the next state
    g: CheckersGraphNode = CheckersGraphNode().set_spec(
        GraphNodeType.MAX)  # type: ignore
    g.state = CheckersState(8, 8)
    init_board(g.state)
    g.run_iterative_deepening_dfs(5)