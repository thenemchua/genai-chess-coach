import chess
import math

# --- Constants ---
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

LICHESS_THRESHOLDS = {
    "blunder": 0.6,
    "mistake": 0.4,
    "inaccuracy": 0.2
}

# --- Utilities ---
def is_sacrifice(board: chess.Board, move: chess.Move) -> bool:
    """
    Detects a material sacrifice: a valuable piece is exposed
    to capture after the move without clear compensation.
    """
    piece = board.piece_at(move.from_square)
    if not piece:
        return False

    board.push(move)
    is_exposed = board.is_attacked_by(not board.turn, move.to_square)
    board.pop()

    return is_exposed and PIECE_VALUES.get(piece.piece_type, 0) >= 3

# --- Chess.com Logic ---
def classify_move_quality_chesscom(
    eval_played: float,
    eval_best: float,
    board: chess.Board,
    move: chess.Move,
    is_best_move=False,
    is_only_good_move=False,
    is_opening_book=False,
) -> str:
    """
    Classifies move quality using a simplified Chess.com-like logic.
    """
    delta = abs(eval_best - eval_played)

    if is_opening_book:
        return "Coup théorique"

    if is_best_move and is_only_good_move:
        return "Coup génial (!)"

    if is_sacrifice(board, move) and delta <= 0.5 and is_best_move and is_only_good_move:
        return "Coup brillant (!!)"

    if is_best_move:
        return "Meilleur coup"

    if delta <= 0.15:
        return "Excellent coup (!)"
    elif delta <= 0.5:
        return "Bon coup"
    elif delta <= 1.0:
        return "Coup douteux (?!?)"
    elif delta <= 3.0:
        return "Erreur (?)"
    elif eval_best > 2.0 and eval_played < 0.5:
        return "Gain manqué (X)"
    else:
        return "Gaffe (??)"

# --- Lichess Logic ---
def eval_to_win_chance(eval_cp: float) -> float:
    """
    Converts a centipawn evaluation to a win probability.
    """
    return 1 / (1 + math.exp(-eval_cp / 100))

def classify_move_quality_lichess(
    eval_played: float,
    eval_best: float,
    is_best_move: bool = False
) -> str:
    """
    Classifies move quality using the Lichess-style approach,
    based on changes in win probability.
    """
    if is_best_move:
        return "Meilleur coup"

    win_chance_best = eval_to_win_chance(eval_best * 100)
    win_chance_played = eval_to_win_chance(eval_played * 100)
    delta = win_chance_best - win_chance_played

    if delta >= LICHESS_THRESHOLDS["blunder"]:
        return "Gaffe (??)"
    elif delta >= LICHESS_THRESHOLDS["mistake"]:
        return "Erreur (?)"
    elif delta >= LICHESS_THRESHOLDS["inaccuracy"]:
        return "Coup douteux (?!?)"
    else:
        return "Bon coup"
    
def classify_move_quality_simplified(
    eval_played: float,
    eval_best: float,
    is_best_move: bool = False
) -> str:
    """
    Classifies move quality using simplified Lichess-style thresholds on centipawn loss.
    """
    delta_cp = abs((eval_best - eval_played) * 100)

    if is_best_move:
        return "Meilleur coup"
    elif delta_cp >= 300:
        return "Gaffe (??)"
    elif delta_cp >= 175:
        return "Erreur (?)"
    elif delta_cp >= 100:
        return "Coup douteux (?!?)"
    else:
        return "Bon coup"