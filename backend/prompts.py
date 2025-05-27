from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
    filename="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    local_dir="models",
    n_ctx=4096,
    n_threads=4,
    n_gpu_layers=33
)

# TACTICAL_GUIDE = """
# Tu peux t’appuyer sur les concepts suivants :
# - Clouage (pin)
# - Fourchette (fork)
# - Rayon X
# - Échec double
# - Batterie
# - Défense surchargée
# - Attaque sur case faible
# - Sacrifice positionnel ou tactique
# - Domination
# - Zugzwang
# - Défense impossible
# - Défense passive / active
# - Contrôle du centre
# - Développement
# - Sécurité du roi
# - Coordination des pièces
# - Initiative / Tempo

# Explique chaque concept utilisé si nécessaire.
# """

TACTICAL_GUIDE = """
Concepts stratégiques :
- Contrôle du centre
- Développement rapide des pièces mineures
- Roque et sécurité du roi
- Amélioration des pièces mal placées
- Occupation de colonnes ouvertes
- Domination de cases clés
- Planification à long terme
- Coordination des pièces
- Avantage d’espace
- Structure de pions (majorité, pions doublés, isolés)

S'il y a lieu: clouage, fourchette, sacrifice, attaque sur case faible, etc."""

def generate_prompt(
    coup: str,
    position_fen: str,
    eval_played: float,
    eval_best: float,
    best_move: str,
    best_line: list,
    quality: str
) -> str:
    """
    Construit dynamiquement un prompt de qualité stratégique pour le LLM,
    basé sur le type de coup et les données issues de Stockfish.
    """

    intro = f"""Tu es un entraîneur français d’échecs expérimenté de niveau GM.
Ton rôle est d’enseigner avec rigueur les décisions prises sur l’échiquier.
Évite les généralisations vagues. Sois précis dans tes justifications.
Utilise des phrases courtes, pédagogiques et sans jargon inutile.

Nous allons analyser le coup {coup} dans la position suivante (FEN) :
{position_fen}

Évaluation après ce coup : {eval_played}
Meilleur coup selon l’ordinateur : {best_move}
Évaluation du meilleur coup : {eval_best}
Ligne principale recommandée : {', '.join(best_line[:8])}

{TACTICAL_GUIDE}
"""

    instruction_map = {
        "Coup brillant (!!)": "Explique pourquoi ce coup est brillant. Est-ce un sacrifice tactique ou stratégique ? Montre l’idée cachée.",
        "Coup génial (!)": "Montre pourquoi ce coup était le seul pour maintenir l’avantage. Quelle menace a-t-il paré ?",
        "Meilleur coup": "Pourquoi ce coup est-il optimal ? Quels principes stratégiques illustre-t-il (initiative, pression, développement…) ?",
        "Excellent coup (!)": "Presque parfait. Montre en quoi il respecte les grands principes d’échecs.",
        "Bon coup": "Analyse un coup raisonnable. Quels sont ses objectifs ? Que manque-t-il par rapport au meilleur coup ?",
        "Imprécision (?!?)": "Un coup imprécis. Quelle idée manquée ? Quelle faiblesse créée ?",
        "Erreur (?)": "Un mauvais coup. Montre ses conséquences négatives. Était-ce une perte de tempo, une faiblesse positionnelle, ou autre ?",
        "Gain manqué (X)": "Un gain net a été raté. Quelle ligne gagnait ? Pourquoi ce coup n’était pas suffisant ?",
        "Gaffe (??)": "Une grosse erreur. Montre immédiatement ce que cela perd (matériel, sécurité du roi, initiative).",
        "Coup théorique": "Ce coup fait partie de la théorie. Explique les grandes lignes du plan associé."
    }

    task = instruction_map.get(quality, "Explique ce que ce coup accomplit et ce qu’il aurait pu faire de mieux.")

    return f"<s>[INST] {intro}\n{task} [/INST]".strip()


def generate_explanation(prompt: str, max_tokens: int = 300) -> str:
    """
    Appelle le LLM pour générer l’explication à partir d’un prompt.
    """
    response = llm(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.7,
        stop=["</s>"]
    )
    return response["choices"][0]["text"].strip()
