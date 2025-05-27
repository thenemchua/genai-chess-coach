import chess
import chess.engine
from typing import Optional
from pathlib import Path

DEFAULT_STOCKFISH_PATH = Path(__file__).resolve().parent.parent / "bin" / "stockfish"

class StockfishEngine:
    """
    Interface to interact with the Stockfish chess engine for evaluating positions
    and suggesting best moves or analyzing played moves.
    """

    def __init__(self, path: str = str(DEFAULT_STOCKFISH_PATH), depth: int = 15, time_limit: Optional[float] = None):
        """Initialize the Stockfish engine.

        Args:
            path (str): Path to the Stockfish binary.
            depth (int): Depth in half-moves for fixed-depth analysis.
            time_limit (float, optional): Time in seconds for timed analysis.
        """
        self.engine = chess.engine.SimpleEngine.popen_uci(path)
        self.depth = depth
        self.time_limit = time_limit

    def close(self):
        """Cleanly close the Stockfish engine process."""
        self.engine.quit()

    def _get_limit(self):
        """Determine whether to use depth or time for engine analysis."""
        if self.time_limit is not None:
            return chess.engine.Limit(time=self.time_limit)
        return chess.engine.Limit(depth=self.depth)

    def _safe_analyse(self, board: chess.Board) -> dict:
        """Safely analyze a board position with exception handling.

        Args:
            board (chess.Board): The current board position.

        Returns:
            dict: Analysis result.
        """
        try:
            return self.engine.analyse(board, self._get_limit())
        except Exception as e:
            print(f"[StockfishEngine] Analyse failed: {e}")
            return {}

    def evaluate_position(self, board: chess.Board) -> Optional[float]:
        """Evaluate a board position and return centipawn score.

        Args:
            board (chess.Board): The board to evaluate.

        Returns:
            float: Evaluation score in centipawns (positive = white is better).
        """
        result = self._safe_analyse(board)
        score = result.get("score")
        if score is None:
            return None
        cp = score.white().score(mate_score=10000)
        return cp / 100 if cp is not None else None

    def get_best_move(self, board: chess.Board) -> Optional[str]:
        """Get the best move from the engine for a given position.

        Args:
            board (chess.Board): The current board state.

        Returns:
            str: Best move in UCI format, or None.
        """
        result = self._safe_analyse(board)
        pv = result.get("pv")
        return pv[0].uci() if pv else None

    def get_best_line(self, board: chess.Board, multipv=1) -> list:
        """Get the principal variation (best line of play).

        Args:
            board (chess.Board): The current position.
            multipv (int): Number of variations to return (default is 1).

        Returns:
            list: List of best moves in UCI format.
        """
        try:
            result = self.engine.analyse(board, self._get_limit(), multipv=multipv)
            return [move.uci() for move in result.get("pv", [])]
        except Exception as e:
            print(f"[StockfishEngine] PV extraction failed: {e}")
            return []

    def analyze_move(self, board: chess.Board, move: chess.Move) -> dict:
        """Compare a played move with Stockfish's best move.

        Args:
            board (chess.Board): The board before the move.
            move (chess.Move): The move played.

        Returns:
            dict: Analysis including evaluations before and after, and best line.
        """
        board_before = board.copy()
        result_before = self._safe_analyse(board_before)
        eval_best = result_before.get("score")
        best_line = [m.uci() for m in result_before.get("pv", [])] if result_before else []
        best_move_obj = result_before.get("pv", [None])[0]
        best_move = best_move_obj.uci() if best_move_obj else None
        best_move_san = board_before.san(best_move_obj) if best_move_obj else None
        eval_best_cp = eval_best.white().score(mate_score=10000) / 100 if eval_best else None # .white is used to ensure we get the score from White's perspective (+ for White, - for Black)

        board_after = board.copy()
        board_after.push(move)
        result_after = self._safe_analyse(board_after)
        eval_played = result_after.get("score")
        eval_played_cp = eval_played.white().score(mate_score=10000) / 100 if eval_played else None

        return {
            "eval_played": eval_played_cp,
            "eval_best": eval_best_cp,
            "best_move": best_move,
            "best_move_san": best_move_san,
            "best_line": best_line,
            "is_best_move": (best_move == move.uci()) if best_move else False,
        }
