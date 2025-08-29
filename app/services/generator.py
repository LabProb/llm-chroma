#app/services/generator.py
from pathlib import Path
from app.llm.llama_wrapper import LlamaModel
from app.config import settings

# === Глобальний екземпляр для сеансу ===
_model_instances: dict[str, LlamaModel] = {}

DEFAULT_STOP = ["User:", "Assistant:", "</s>"]
DEFAULT_PARAMS = {
    "max_tokens": 256,
    "temperature": 0.8,
    "top_p": 0.9,
    "repeat_penalty": 1.2,
    "stop": DEFAULT_STOP
}

def list_models() -> list[str]:
    if not settings.model_dir.exists():
        return []
    return [f.name for f in sorted(settings.model_dir.glob("*.gguf"))]

def build_prompt(user_input: str) -> str:
    return (
        "You are a concise assistant.\n"
        f"User: {user_input}\n"
        "Assistant:"
    )

def get_model(model_name: str | None = None) -> LlamaModel:
    key = model_name or settings.model_name
    if key not in _model_instances:
        _model_instances[key] = LlamaModel(model_path=settings.model_dir / key)
    return _model_instances[key]

def generate_response(
    user_input: str,
    model_name: str | None = None,
    max_tokens: int = DEFAULT_PARAMS["max_tokens"],
    temperature: float = DEFAULT_PARAMS["temperature"],
    top_p: float = DEFAULT_PARAMS["top_p"],
    repeat_penalty: float = DEFAULT_PARAMS["repeat_penalty"],
) -> tuple[str, int]:
    """Генеруємо відповідь через глобальний екземпляр моделі з можливістю передати параметри."""
    prompt = build_prompt(user_input)
    model = get_model(model_name)

    # Оновлюємо поточні параметри
    model.set_params(
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        repeat_penalty=repeat_penalty,
        stop=DEFAULT_PARAMS["stop"]
    )

    return model.generate(prompt)
