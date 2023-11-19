import chess

PAWN_VALUE = 100
KNIGHT_VALUE = 300
BISHOP_VALUE = 300
ROOK_VALUE = 500
QUEEN_VALUE = 900


def get_legal_moves(board):
    return list(board.legal_moves)


def evaluate_position(board):
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 10000
    }

    pawn_table = [
        0,   0,   0,   0,   0,   0,   0,   0,
        50,  50,  50,  50,  50,  50,  50,  50,
        10,  10,  20,  30,  30,  20,  10,  10,
        5,   5,  10,  25,  25,  10,   5,   5,
        0,   0,   0,  20,  20,   0,   0,   0,
        5,  -5, -10,   0,   0, -10,  -5,   5,
        5,  10,  10, -20, -20,  10,  10,   5,
        0,   0,   0,   0,   0,   0,   0,   0
    ]

    rook_table = [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]

    knight_table = [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20,  0,  0,  0,  0, -20, -40,
        -30,  0, 10, 15, 15, 10,  0, -30,
        -30,  5, 15, 20, 20, 15,  5, -30,
        -30,  0, 15, 20, 20, 15,  0, -30,
        -30,  5, 10, 15, 15, 10,  5, -30,
        -40, -20,  0,  5,  5,  0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50,
    ]

    bishop_table = [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10,  0,  0,  0,  0,  0,  0, -10,
        -10,  0,  5, 10, 10,  5,  0, -10,
        -10,  5,  5, 10, 10,  5,  5, -10,
        -10,  0, 10, 10, 10, 10,  0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10,  5,  0,  0,  0,  0,  5, -10,
        -20, -10, -10, -10, -10, -10, -10,
        -20,
    ]

    queen_table = [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10,  0,  0,  0,  0,  0,  0, -10,
        -10,  0,  5,  5,  5,  5,  0, -10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0, -10,
        -10,  0,  5,  0,  0,  0,  0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20
    ]

    king_table = [
        -80, -70, -70, -70, -70, -70, -70, -80,
        -60, -60, -60, -60, -60, -60, -60, -60,
        -40, -50, -50, -60, -60, -50, -50, -40,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, -5, -5, -5, -5, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20
    ]

    positional_values = {
        chess.PAWN: pawn_table,
        chess.KNIGHT: knight_table,
        chess.BISHOP: bishop_table,
        chess.ROOK: rook_table,
        chess.QUEEN: queen_table,
        chess.KING: king_table
    }

    total_value = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            # Basic piece value
            value = piece_values.get(piece.piece_type, 0)

            # Positional value
            if piece.color == chess.WHITE:
                position_value = positional_values[piece.piece_type][square]
                total_value += value + position_value
            else:
                # Flip the table for black
                position_value = positional_values[piece.piece_type][63 - square]
                total_value -= value + position_value

    return total_value * 0.01


def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_position(board)

    if maximizing_player:
        max_eval = -float('inf')
        for move in get_legal_moves(board):
            board.push(move)
            eval = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_legal_moves(board):
            board.push(move)
            eval = minimax_alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def get_best_move(board, depth):
    best_move = None
    alpha = -float('inf')
    beta = float('inf')

    if board.turn == chess.WHITE:
        best_score = -float('inf')
        for move in get_legal_moves(board):
            board.push(move)
            score = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
    else:
        best_score = float('inf')
        for move in get_legal_moves(board):
            board.push(move)
            score = minimax_alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            if score < best_score:
                best_score = score
                best_move = move

    return best_move
