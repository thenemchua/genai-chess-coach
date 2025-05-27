import chess.pgn
from pathlib import Path
from backend.stockfish_engine import StockfishEngine
from backend.prompts import generate_prompt, generate_explanation
from backend.utils import classify_move_quality_simplified


def analyze_pgn(pgn_path: str, max_moves: int = None) -> list:
    """
    Analyze a PGN game move by move, using Stockfish for evaluation and a LLM for explanations.
    """
    pgn_file = Path(pgn_path)

    if not pgn_file.exists():
        raise FileNotFoundError(f"Fichier PGN introuvable: {pgn_path}")

    with open(pgn_file, encoding="utf-8") as f:
        game = chess.pgn.read_game(f)

    board = game.board()
    engine = StockfishEngine()
    results = []

    all_moves = list(game.mainline_moves())
    if max_moves is None:
        max_moves = len(all_moves)
    moves = all_moves[:max_moves]

    for move in moves:
        move_san = board.san(move)
        fen = board.fen()

        # Stockfish analysis
        analysis = engine.analyze_move(board, move)
        quality = classify_move_quality_simplified(
            eval_played=analysis["eval_played"],
            eval_best=analysis["eval_best"],
            is_best_move=analysis["is_best_move"]
        )
        
        # UCI to SAN conversion for best line
        best_line_san = []
        tmp_board = board.copy()
        for move_uci in analysis.get("best_line", []):
            move_obj = chess.Move.from_uci(move_uci)
            if move_obj in tmp_board.legal_moves:
                best_line_san.append(tmp_board.san(move_obj))
                tmp_board.push(move_obj)
            else:
                break # Stop if the move is illegal (should not happen in a valid analysis)

        # Prompt generation and LLM explanation
        prompt = generate_prompt(
            coup=move_san,
            position_fen=fen,
            eval_played=analysis["eval_played"],
            eval_best=analysis["eval_best"],
            best_move=analysis["best_move"],
            best_line=best_line_san,
            quality=quality
        )

        try:
            explanation = generate_explanation(prompt)
        except Exception as e:
            explanation = f"[Erreur Mistral] {e}"

        results.append({
            "coup": move_san,
            "fen": fen,
            "eval": analysis["eval_played"],
            "best_move": analysis["best_move"],
            "best_move_san": analysis["best_move_san"],
            "best_line": best_line_san,
            "quality": quality,
            "analyse": explanation
        })

        board.push(move)

    engine.close()
    return results


if __name__ == "__main__":
    from pprint import pprint
    analyses = analyze_pgn("games/game1.pgn", max_moves=2)
    pprint(analyses)
