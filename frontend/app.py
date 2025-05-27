import streamlit as st
import chess
import chess.pgn
import chess.svg
import io
from PIL import Image
import cairosvg
from backend.analyzer import analyze_pgn

# --- Page Setup ---
st.set_page_config(page_title="Analyse d'échecs IA", layout="wide")

# --- Session State Init ---
st.session_state.setdefault("pgn_file", None)
st.session_state.setdefault("analysis", [])
st.session_state.setdefault("moves", [])
st.session_state.setdefault("current_index", 0)
st.session_state.setdefault("game_loaded", False)

# --- Sidebar ---
st.sidebar.title("♟️ Analyse ta partie d'échecs")
uploaded_file = st.sidebar.file_uploader("Téléverse un fichier PGN", type=["pgn"])

if uploaded_file and not st.session_state.game_loaded:
    pgn_path = "games/_uploaded_game.pgn"
    with open(pgn_path, "wb") as f:
        f.write(uploaded_file.read())

    try:
        st.session_state.analysis = analyze_pgn(pgn_path, max_moves=5)

        # Load moves directly from PGN to sync with board
        with open(pgn_path, encoding="utf-8") as f:
            game = chess.pgn.read_game(f)
            st.session_state.moves = list(game.mainline_moves())

        st.session_state.current_index = 0
        st.session_state.game_loaded = True
    except Exception as e:
        st.error(f"Erreur pendant l’analyse : {e}")

# --- Layout Styling ---
st.markdown("""
    <style>
    .title {
        text-align: center;
        color: #ffffff;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .board-column {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 1rem;
    }
    .analysis-box {
        background-color: #262421;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #444;
        color: white;
        font-size: 1rem;
    }
    .highlight {
        color: #ffd700;
        font-weight: bold;
    }
    .nav-buttons button {
        background-color: #1a1a1a;
        color: white;
        font-size: 1rem;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>Analyse stratégique assistée par IA</div>", unsafe_allow_html=True)

# --- Main Columns ---
left_col, right_col = st.columns([2, 3])

# --- Navigation Buttons (above board) ---
with left_col:
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])
    with btn_col1:
        if st.button("⟲ Début"):
            st.session_state.current_index = 0
    with btn_col2:
        if st.button("← Précédent") and st.session_state.current_index > 0:
            st.session_state.current_index -= 1
    with btn_col3:
        if st.button("Suivant →") and st.session_state.current_index < len(st.session_state.analysis):
            st.session_state.current_index += 1
    with btn_col4:
        if st.button("Fin ⟳"):
            st.session_state.current_index = len(st.session_state.analysis)

    # --- Board Rendering ---
    board = chess.Board()
    for move in st.session_state.moves[:st.session_state.current_index]:
        board.push(move)

    svg_board = chess.svg.board(board=board, size=500)
    png = cairosvg.svg2png(bytestring=svg_board)
    image = Image.open(io.BytesIO(png))
    st.image(image, use_container_width=True)

# --- Analysis Panel ---
with right_col:
    if st.session_state.analysis and st.session_state.current_index > 0:
        analysis = st.session_state.analysis[st.session_state.current_index - 1]
        st.markdown(f"""
        <div class="analysis-box">
            <h4>Analyse du coup</h4>
            <p><span class="highlight">Coup joué :</span> {analysis['coup']}</p>
            <p><span class="highlight">Évaluation :</span> {analysis['eval']}</p>
            <p><span class="highlight">Meilleur coup :</span> {analysis['best_move_san']}</p>
            <p><span class="highlight">Catégorie :</span> {analysis['quality']}</p>
            <p><span class="highlight">Ligne principale :</span> {' → '.join(analysis['best_line'][:8])}</p>
            <hr>
            <p>{analysis['analyse']}</p>
        </div>
        """, unsafe_allow_html=True)
