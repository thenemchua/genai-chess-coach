from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
    filename="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    local_dir="models",
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=33
)

def build_prompt(coup: str, position_fen: str, niveau: str = "débutant") -> str:
    """
    Construit un prompt pour expliquer un coup d’échecs à un certain niveau.
    """
    prompt = f"""
            Tu es un coach d’échecs parlant à un joueur de niveau {niveau}.
            Sois pédagogique, clair et bienveillant.

            Explique pourquoi le coup suivant est une erreur dans la position donnée.

            - Position FEN : {position_fen}
            - Coup joué : {coup}
            """
    return prompt.strip()

def generate_explanation(prompt: str, max_tokens: int = 300) -> str:
    """
    Génère une explication textuelle à partir d’un prompt.
    """
    output = llm(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.7,
        stop=["</s>"]
    )
    return output["choices"][0]["text"].strip()
