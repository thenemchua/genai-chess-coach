from prompts import build_prompt, generate_explanation

prompt = build_prompt(
    coup="Qxf7+",
    position_fen="r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
    niveau="débutant"
)

print("Génération en cours...\n")
explication = generate_explanation(prompt)
print("Coach IA :\n", explication)