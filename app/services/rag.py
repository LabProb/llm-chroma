# app/services/rag.py

import os
import logging
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv, find_dotenv
from chromadb import PersistentClient

from app.llm.llama_wrapper import LlamaModel
from app.services.generator import DEFAULT_PARAMS   # <-- беремо дефолти звідти

# --------------------------
# 1. Логування
# --------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# --------------------------
# 2. Завантажуємо .env
# --------------------------
env_path = find_dotenv(usecwd=True)
if env_path:
    load_dotenv(env_path)
    logger.info(f"Loaded .env from {env_path}")
else:
    logger.warning(".env file not found – використовуємо системні змінні")

# --------------------------
# 3. Persistent ChromaDB
# --------------------------
project_root = Path(__file__).parent.parent.parent
_chroma_store = os.getenv("CHROMA_STORE")
persist_dir = Path(_chroma_store).expanduser().resolve() if _chroma_store else (project_root / "chroma_store").resolve()
persist_dir.mkdir(parents=True, exist_ok=True)
logger.info(f"ChromaDB persist directory → {persist_dir}")

# Підключаємося через PersistentClient до тієї ж бази, що і txt_to_chroma.py
chroma_client = PersistentClient(path=str(persist_dir))

# --------------------------
# 4. Колекція
# --------------------------
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "text_chunks")
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
logger.info(f"Using ChromaDB collection: `{COLLECTION_NAME}`")

# --------------------------
# 5. Шлях до моделей Llama
# --------------------------
models_dir = project_root / "models"
logger.info(f"Resolved models directory → {models_dir}")
DEFAULT_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH")


def _resolve_model_path(path: str) -> str:
    p = Path(path)
    if p.is_absolute() and p.exists():
        return str(p.resolve())
    alt = models_dir / path
    if alt.exists():
        return str(alt.resolve())
    raise FileNotFoundError(f"Model path does not exist: {path}")


# --------------------------
# 6. Функції
# --------------------------
def retrieve_context(query: str, k: int = 3) -> List[str]:
    """
    Повертає k найрелевантніших chunk’ів із ChromaDB та лог.
    """
    try:
        results = collection.query(query_texts=[query], n_results=k)
        docs = results.get("documents", [])
        if docs:
            logger.info(f"ChromaDB retrieved {len(docs[0])} documents for query: {query}")
            for i, d in enumerate(docs[0], 1):
                logger.info(f"[doc {i}] {d[:100]}...")
            return docs[0]
        else:
            logger.info("ChromaDB returned no documents.")
            return []
    except Exception as e:
        logger.error(f"ChromaDB query error: {e}")
        return []


def generate_with_rag(
    prompt: str,
    model_path: Optional[str] = None,
    max_tokens: int = DEFAULT_PARAMS["max_tokens"],
    temperature: float = DEFAULT_PARAMS["temperature"],
    top_p: float = DEFAULT_PARAMS["top_p"],
    repeat_penalty: float = DEFAULT_PARAMS["repeat_penalty"],
    k: int = 2,  # трохи менше за замовчуванням
) -> dict:
    context_chunks = retrieve_context(prompt, k=k)
    context = "\n\n".join(context_chunks) if context_chunks else "Немає релевантного контексту."

    full_prompt = (
        "You are a helpful assistant.\n"
        "Use ONLY the CONTEXT section below to answer the QUESTION.\n"
        "Do NOT invent facts. If the context does not contain the answer, reply exactly:\n"
        "\"No relevant information.\"\n\n"
        "--- CONTEXT ---\n"
        f"{context}\n\n"
        "--- QUESTION ---\n"
        f"{prompt}\n\n"
        "--- ANSWER ---\n"
    )

    logger.info(f"FULL PROMPT (truncated to 1000 chars):\n{full_prompt[:1000]}...\n")

    mp = model_path or DEFAULT_MODEL_PATH
    if not mp:
        raise RuntimeError("Model path not provided via request or LLAMA_MODEL_PATH env")
    resolved_mp = _resolve_model_path(mp)

    model = LlamaModel(model_path=resolved_mp)

    # Перша спроба: без стоп-символів (щоб уникнути миттєвої зупинки),
    # інструкція нижче дає LLM більше шансів.
    answer, tokens = model.generate(
        full_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        repeat_penalty=repeat_penalty,
        # stop=[]  # llama_wrapper вже перетворить None -> []
    )

    if not answer.strip():
        logger.warning("Empty answer from first generation — retrying with higher temperature and more tokens.")
        # Друга спроба: підвищимо temperature і max_tokens, прибираємо stop
        answer2, tokens2 = model.generate(
            full_prompt,
            max_tokens=min(1024, max_tokens * 2),
            temperature=max(0.35, temperature + 0.15),
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            # stop=[]
        )
        if answer2.strip():
            answer, tokens = answer2, tokens2

    if not answer.strip():
        logger.warning("LLM returned empty answer after retries.")
        answer = "LLM returned empty answer — context was provided but model produced no text."

    return {"answer": answer, "context": context_chunks, "tokens": tokens}


__all__ = ["retrieve_context", "generate_with_rag"]
